#!/usr/bin/env python3
"""A tiny iOS Shortcuts bridge for Veglia.

Standard library only. It remembers App open/close events, emits one watch hook
after a session crosses a time limit, and sends a summon email on request.
"""
from __future__ import annotations

import argparse
import hmac
import json
import os
import shlex
import smtplib
import subprocess
import sys
import time
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import RLock, Thread
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
VERSION = "0.1.0"
MAX_BODY = 4096
EVENT_WINDOW = 2 * 60 * 60
EVENT_MAX = 100


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_dotenv(HERE / ".env")


class Config:
    def __init__(self) -> None:
        self.token = os.getenv("VEGLIA_TOKEN", "").strip()
        self.host = os.getenv("VEGLIA_HOST", "127.0.0.1")
        self.port = int(os.getenv("VEGLIA_PORT", "8513"))
        data_dir = os.getenv("VEGLIA_DATA_DIR", str(HERE / "data"))
        self.data_dir = Path(data_dir).expanduser().resolve()
        self.watch_after = max(1.0, float(os.getenv("VEGLIA_WATCH_AFTER_MIN", "15")))
        self.watch_hook = os.getenv("VEGLIA_WATCH_HOOK", "").strip()
        self.smtp_host = os.getenv("SMTP_HOST", "").strip()
        self.smtp_port = int(os.getenv("SMTP_PORT", "465"))
        self.smtp_user = os.getenv("SMTP_USER", "").strip()
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.mail_to = os.getenv("SUMMON_MAIL_TO", "").strip()
        self.summon_subject = os.getenv("VEGLIA_SUMMON_SUBJECT", "[Veglia] Summon")


class Store:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.lock = RLock()
        self.data = self._load()

    def _load(self) -> dict:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (OSError, ValueError):
            pass
        return {"current": None, "events": []}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        temporary.replace(self.path)

    def record(self, app: str, event: str, now: float | None = None) -> dict:
        now = time.time() if now is None else now
        app = " ".join(str(app).split())[:80]
        event = str(event).lower()
        if not app or event not in {"open", "close"}:
            raise ValueError("app is required; event must be open or close")
        with self.lock:
            current = self.data.get("current")
            if event == "open":
                if current and current.get("app") == app:
                    return self.status(now)
                if current:
                    self.data["events"].append({
                        "ts": now, "app": current["app"], "event": "close"
                    })
                self.data["current"] = {
                    "app": app, "opened_at": now, "watch_claimed": False
                }
            elif current and current.get("app") == app:
                self.data["current"] = None
            self.data["events"].append({"ts": now, "app": app, "event": event})
            cutoff = now - EVENT_WINDOW
            self.data["events"] = [
                item for item in self.data["events"] if item.get("ts", 0) >= cutoff
            ][-EVENT_MAX:]
            self._save()
            return self.status(now)

    def status(self, now: float | None = None) -> dict:
        now = time.time() if now is None else now
        with self.lock:
            current = self.data.get("current")
            if not current:
                return {"current": None, "events": list(self.data.get("events", []))}
            active = dict(current)
            active["seconds"] = max(0, int(now - float(active["opened_at"])))
            return {"current": active, "events": list(self.data.get("events", []))}

    def claim_due(self, after_minutes: float, now: float | None = None) -> dict | None:
        now = time.time() if now is None else now
        with self.lock:
            current = self.data.get("current")
            if not current or current.get("watch_claimed"):
                return None
            seconds = max(0, now - float(current["opened_at"]))
            if seconds < after_minutes * 60:
                return None
            current["watch_claimed"] = True
            self._save()
            return {
                "type": "app_watch",
                "app": current["app"],
                "minutes": max(1, int(seconds // 60)),
                "opened_at": current["opened_at"],
            }


CONFIG = Config()
STORE = Store(CONFIG.data_dir / "state.json")


def token_ok(handler: BaseHTTPRequestHandler) -> bool:
    query = parse_qs(urlparse(handler.path).query)
    supplied = handler.headers.get("X-Auth-Token", "") or query.get("token", [""])[0]
    return bool(CONFIG.token) and hmac.compare_digest(supplied, CONFIG.token)


class Handler(BaseHTTPRequestHandler):
    def json_response(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/health"}:
            self.json_response(200, {"ok": True, "service": "veglia-ios", "version": VERSION})
            return
        if path == "/phone/activity" and token_ok(self):
            self.json_response(200, {"ok": True, **STORE.status()})
            return
        self.json_response(403 if path == "/phone/activity" else 404, {"error": "not_found_or_denied"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/phone/activity":
            self.json_response(404, {"error": "not_found"})
            return
        if not token_ok(self):
            self.json_response(403, {"error": "bad_token"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > MAX_BODY:
                raise ValueError("bad body size")
            body = json.loads(self.rfile.read(length))
            status = STORE.record(body.get("app", ""), body.get("event", ""))
        except (ValueError, json.JSONDecodeError) as error:
            self.json_response(400, {"error": str(error)})
            return
        self.json_response(200, {"ok": True, **status})

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("[veglia-ios] %s\n" % (fmt % args))


def run_watch_hook(payload: dict) -> None:
    if not CONFIG.watch_hook:
        return
    env = dict(os.environ)
    raw = json.dumps(payload, ensure_ascii=False)
    env["VEGLIA_EVENT_JSON"] = raw
    try:
        result = subprocess.run(
            shlex.split(CONFIG.watch_hook), input=raw, text=True, env=env,
            timeout=120, check=False,
        )
        print(f"watch hook exited {result.returncode}: {raw}")
    except Exception as error:
        print(f"watch hook failed: {error}", file=sys.stderr)


def watch_loop() -> None:
    while True:
        time.sleep(30)
        if not CONFIG.watch_hook:
            continue
        payload = STORE.claim_due(CONFIG.watch_after)
        if payload:
            run_watch_hook(payload)


def send_summon(reason: str = "") -> None:
    required = [CONFIG.smtp_host, CONFIG.smtp_user, CONFIG.smtp_password, CONFIG.mail_to]
    if not all(required):
        raise RuntimeError("set SMTP_HOST, SMTP_USER, SMTP_PASSWORD and SUMMON_MAIL_TO")
    message = EmailMessage()
    message["From"] = CONFIG.smtp_user
    message["To"] = CONFIG.mail_to
    message["Subject"] = CONFIG.summon_subject
    message.set_content(reason.strip() or "Your companion is calling you back.")
    with smtplib.SMTP_SSL(CONFIG.smtp_host, CONFIG.smtp_port, timeout=20) as smtp:
        smtp.login(CONFIG.smtp_user, CONFIG.smtp_password)
        smtp.send_message(message)
    print("sent summon")


def serve() -> None:
    if not CONFIG.token:
        raise SystemExit("set VEGLIA_TOKEN in server/.env first")
    Thread(target=watch_loop, daemon=True).start()
    server = ThreadingHTTPServer((CONFIG.host, CONFIG.port), Handler)
    print(f"Veglia iOS bridge {VERSION} on http://{CONFIG.host}:{CONFIG.port}")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("serve")
    sub.add_parser("status")
    summon_parser = sub.add_parser("summon")
    summon_parser.add_argument("--reason", default="")
    args = parser.parse_args()
    if args.command == "serve":
        serve()
    elif args.command == "status":
        print(json.dumps(STORE.status(), ensure_ascii=False, indent=2))
    else:
        send_summon(args.reason)


if __name__ == "__main__":
    main()


