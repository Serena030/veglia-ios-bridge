# Véglia iOS Bridge

感谢 **Evelyn & River** 的 [Véglia](https://github.com/sebastianevan200-stack/veglia)——原版只有 Android，我们在他们的启发下做了这个 iOS 版本。

iPhone 上报你正在用什么 App、用了多久，超时了可以自动把你召回到指定的 App 或网页。iOS 没有 Android 那种后台截图能力，所以这个桥只做两件事：**上报 App 状态**和**召回**。

## 它做了什么

```text
你打开某个 App
  → iPhone 快捷指令自动 POST 到你的服务器
  → 服务器开始计时
  → 连续用了 15 分钟
  → 触发你设置的 hook（比如让 AI 判断要不要召回）
  → 服务器发一封邮件
  → iPhone 收到邮件，自动打开指定的 App 或网页
```

整个过程只在 hook 这一步可能产生一次调用（取决于你怎么接），邮件、上报、计时都不经过模型。

## 你需要准备什么

- 一台 VPS（或任何能跑 Python、能被手机访问到的服务器）
- Python 3.10+
- **两个邮箱**
- 一台 iPhone

### 为什么要两个邮箱

一个**发送邮箱**，给服务器后端用，负责发控制邮件。建议用小号。（我们推荐QQ邮箱）

一个**接收邮箱**，加到你 iPhone 的系统「邮件」App 里。iPhone 的快捷指令自动化会监听这个邮箱——收到特定主题的邮件就自动执行动作。

发件和收件必须是不同地址。iPhone 的邮件自动化触发的是「收到新邮件」，不是「发送邮件」，所以自己给自己发是不行的。

## 第一步：拿到邮箱的 SMTP 授权码

你的服务器需要用 SMTP 协议发邮件，这边以QQ邮箱为例子，QQ 邮箱不允许直接用登录密码发，需要单独生成一个授权码。

1. 用电脑打开 QQ 邮箱网页版
2. 进入「设置 → 账户」
3. 找到「POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV 服务」
4. 开启「POP3/SMTP 服务」或「IMAP/SMTP 服务」（开哪个都行，我们只用 SMTP）
5. 按提示用手机发短信验证
6. 验证完会给你一个**授权码**——复制下来，只会显示一次

这个授权码就是你填进 `.env` 的 `SMTP_PASSWORD`，不是你的 QQ 密码。

## 第二步：配置服务器

```bash
git clone https://github.com/Serena030/veglia-ios-bridge.git
cd veglia-ios-bridge/server
cp .env.example .env
```

生成一个 token（iPhone 和服务器之间的共享密钥，防止别人乱发请求）：

```bash
head -c 24 /dev/urandom | base64
```

编辑 `.env`：

```dotenv
# iPhone 和服务器共享的密钥，自己生成一个长随机字符串
VEGLIA_TOKEN=刚才生成的那串

# 发送邮箱（小号）的 SMTP 配置
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=你的发送邮箱@qq.com
SMTP_PASSWORD=刚才拿到的授权码

# iPhone 上的接收邮箱
SUMMON_MAIL_TO=你的接收邮箱

# 连续用多久触发 AI 判断（分钟）
VEGLIA_WATCH_AFTER_MIN=15
```

> `.env` 文件不要截图、不要提交到 Git。

锁一下权限：

```bash
chmod 600 .env
```

启动：

```bash
python3 veglia_ios.py serve
```

默认监听 `127.0.0.1:8513`。如果要让 iPhone 从公网访问，前面套一层 nginx 或 Caddy，配好 HTTPS。不要把裸 HTTP 直接暴露。

测试一下能不能通：

```bash
curl http://127.0.0.1:8513/health
```

看到 `{"ok": true}` 就行。

## 第三步：iPhone 接收邮箱

把你的接收邮箱添加到 iPhone 系统自带的「邮件」App 里：

- 打开 iPhone「设置 → 邮件 → 账户 → 添加账户」
- 如果是 QQ 邮箱，选「其他」，填 IMAP 配置
- 如果是 iCloud 邮箱，直接用 Apple ID 登录就有

添加完之后，去「邮件」App 里确认能收到邮件。

## 第四步：创建快捷指令和自动化

你需要建三组东西。全部在 iPhone 的「快捷指令」App 里操作。

### 4.1 App 打开时上报

「快捷指令 → 自动化 → 右上角 + → App」

- 选一个你想监控的 App（比如小红书），勾选「打开时」
- 动作选「获取 URL 内容」
- URL 填 `https://你的域名/phone/activity`
- 方法选 `POST`
- 请求正文选 `JSON`
- 添加字段 `app`，值填 App 名（比如 `小红书`）
- 添加字段 `event`，值填 `open`
- 添加请求头 `X-Auth-Token`，值填你的 token
- 运行方式选「立即运行」，关掉「运行前询问」

### 4.2 App 关闭时上报

复制上面那条自动化，改两个地方：

- 触发条件改成「关闭时」
- `event` 的值改成 `close`

这里的「关闭」是离开这个 App（切到别的或回桌面），不需要杀进程。

> 先只给一个 App 建，跑通了再加别的。一次勾太多 App 出了问题不好排查。

### 4.3 收到邮件时召回

先建一个普通快捷指令：

- 名字随便起，比如「Véglia Summon」
- 如果你要召回到**原生 App**：添加动作「打开 App」→ 选目标 App
- 如果你要召回到**网页**：添加动作「打开 URL」→ 填网页地址（比如 `https://你的域名`）
- 手动跑一次，确认能切过去

再建一条邮件自动化：

- 「快捷指令 → 自动化 → 右上角 + → 电子邮件」
- 发件人填你的**发送邮箱**
- 主题包含 `[Veglia] Summon`（和 `.env` 里的 `VEGLIA_SUMMON_SUBJECT` 一致）
- 动作选「运行快捷指令」→ 选刚才建的「Véglia Summon」
- 「立即运行」，关掉「运行前询问」

> 网页版的话，建议先把网页「添加到主屏幕」，这样召回时会像打开 App 一样全屏显示，而不是在 Safari 里开一个标签页。

## 第五步：测试

### 测上报

打开你监控的那个 App，然后在服务器上看：

```bash
python3 veglia_ios.py status
```

应该能看到 `current.app` 是那个 App，`seconds` 在涨。离开 App 后 `current` 变成 `null`。

### 测召回

```bash
python3 veglia_ios.py summon --reason "回来"
```

终端显示 `sent summon` 之后等一会，iPhone 应该会自动切到目标 App 或网页。邮件链路有几十秒延迟是正常的。

### 跑测试

```bash
python3 -m unittest test_veglia_ios.py
```

这个不联网，纯本地。

## 第六步：接入 hook

到这一步，上报和召回的链路已经通了。接下来设置 hook——当某个 App 连续使用超过阈值时，服务器会调用你指定的脚本。你可以在脚本里做任何事：发通知、调用 AI、写日志，或者直接召回。

在 `.env` 里设置 `VEGLIA_WATCH_HOOK`，指向你的脚本。事件 JSON 会写进 stdin：

```json
{"type": "app_watch", "app": "小红书", "minutes": 15, "opened_at": 1788432000}
```

你的脚本拿到这个事件后自行决定下一步。需要召回时执行：

```bash
python3 /绝对路径/veglia_ios.py summon --reason "回来"
```

详见 [docs/ai-integration.md](docs/ai-integration.md)。

### 关于开销

- App 上报、计时、发邮件：**不调用模型，零开销**
- hook 里做什么取决于你——如果接了 AI，每个 App 会话最多触发一次调用
- 同一个 App 会话只触发一次，不会反复调用

## 隐私

只上报 App 名和开/关事件。不截图，不录屏，不读取 App 内容。

召回会打断你正在做的事，所以你随时可以去「快捷指令 → 自动化」里关掉它。

## 配置一览

| 变量 | 默认 | 说明 |
|---|---:|---|
| `VEGLIA_TOKEN` | 必填 | 共享密钥 |
| `VEGLIA_HOST` | `127.0.0.1` | 监听地址 |
| `VEGLIA_PORT` | `8513` | 监听端口 |
| `VEGLIA_DATA_DIR` | `server/data` | 状态目录 |
| `VEGLIA_WATCH_AFTER_MIN` | `15` | 触发判断的分钟数 |
| `VEGLIA_WATCH_HOOK` | 空 | 事件处理脚本 |
| `SMTP_HOST` / `SMTP_PORT` | 空 / `465` | SMTP 服务 |
| `SMTP_USER` / `SMTP_PASSWORD` | 空 | 发送邮箱和授权码 |
| `SUMMON_MAIL_TO` | 空 | iPhone 接收邮箱 |
| `VEGLIA_SUMMON_SUBJECT` | `[Veglia] Summon` | 邮件主题 |

## 和原版 Véglia 的区别

| | Android 原版 | iOS Bridge |
|---|---|---|
| 感知前台 App | AccessibilityService | 快捷指令自动化 |
| 截图 | 支持 | 不支持 |
| 召回 | App 轮询命令队列 | 邮件触发快捷指令 |
| 延迟 | 几秒 | 几十秒 |

## 硬限制

- iPhone 必须处于已解锁状态，快捷指令不能绕过锁屏
- 邮件到达速度取决于邮箱推送，不是实时的
- 首次运行时 iOS 可能会弹权限确认

## 来源与许可

受 **Evelyn & River** 的 [Véglia](https://github.com/sebastianevan200-stack/veglia) 启发。用快捷指令和邮件替代了 Android 的 AccessibilityService，加了会话计时和 SMTP 召回，去掉了截图。

**CC BY-NC-SA 4.0** — 署名、非商业、相同方式共享。见 [LICENSE](LICENSE)。
