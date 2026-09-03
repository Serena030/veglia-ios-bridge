# V茅glia iOS Bridge锛堥潪瀹樻柟锛?
> An unofficial iOS Shortcuts bridge inspired by [V茅glia](https://github.com/sebastianevan200-stack/veglia).

鐢?**iOS 蹇嵎鎸囦护 + 閭欢鑷姩鍖?+ 鑷墭绠?Python 鏈嶅姟**锛屾妸 iPhone 涓婄殑 App
浣跨敤鐘舵€佷氦缁欎綘鐨?AI 浼翠荆锛屽苟鍏佽瀹冨湪浣犲仠鐣欏お涔呮椂鎶婁即渚?App 鍙洖鍓嶅彴銆?
杩欎笉鏄師浣滆€呯淮鎶ょ殑瀹樻柟 iOS 鐗堟湰锛屼篃涓嶆槸 Android 鐗堢殑绛変环绉绘銆俰OS 涓嶅厑璁告櫘閫?绗笁鏂瑰簲鐢ㄥ儚 Android AccessibilityService 閭ｆ牱鍦ㄥ悗鍙伴潤榛樻埅鍥撅紱鏈」鐩彧瀹炵幇
鏂囧瓧鐘舵€佷笂鎶ュ拰鐢ㄦ埛鏄庣‘寮€鍚殑 `summon`銆?
## 鍏堣娓呮锛氬悓鎰忥紝涓嶆槸鐩戣

杩欎釜妗ュ彧搴旇瀹夎鍦?*鎵嬫満鎵€鏈夎€呮湰浜虹煡鎯呭苟涓诲姩閰嶇疆**鐨勮澶囦笂銆俙summon` 浼氭墦鏂?褰撳墠鎿嶄綔锛屾墍浠ュ畠蹇呴』鏄竴椤瑰彲浠ラ殢鏃跺叧闂殑鏄庣‘鎺堟潈锛岃€屼笉鏄儵缃氭垨鎺у埗鎵嬫銆?
榛樿娴佺▼涓嶈鍙栨埅鍥撅細

- App 鎵撳紑/鍏抽棴锛氬彧涓婁紶 App 鍚嶃€佷簨浠剁被鍨嬪拰鏈嶅姟鍣ㄦ椂闂淬€?- 鍚庡彴璁℃椂锛氬彧璇绘湰鍦?JSON锛屼笉璋冪敤妯″瀷銆?- `summon`锛氬彧鍙戜竴灏佸浐瀹氫富棰橀偖浠讹紝涓嶈皟鐢ㄦā鍨嬨€?- 鍙湁鈥滆 AI 鍐冲畾瑕佷笉瑕佸彫鍥炩€濊繖涓€姝ヤ細浜х敓涓€娆℃ā鍨嬭皟鐢ㄣ€?
## 瀹冩€庢牱宸ヤ綔

```text
iPhone App 鑷姩鍖?  鈫?POST /phone/activity
  鈫?VPS 璁板綍褰撳墠 App 鍜屽紑濮嬫椂闂?  鈫?婊?15 鍒嗛挓瑙﹀彂涓€娆?VEGLIA_WATCH_HOOK
  鈫?浣犵殑 AI锛氳涓€鍙?/ summon / 涓よ€呴兘鍋?/ 鏆備笉鎵撴壈
  鈫?python3 veglia_ios.py summon
  鈫?閭欢鑷姩鍖栬繍琛屻€屾墦寮€ App銆嶅揩鎹锋寚浠?```

閭欢鎺ㄩ€佸苟闈炲疄鏃跺崗璁紝鐪熸満涓婂嚭鐜板嚑鍗佺寤惰繜鏄甯哥幇璞°€?
## 鐩綍

```text
server/veglia_ios.py       # 闆朵緷璧栨湇鍔°€佺姸鎬?CLI銆乻ummon 閭欢
server/.env.example        # 閰嶇疆妯℃澘
server/test_veglia_ios.py  # 涓嶈仈缃戠殑鍗曞厓娴嬭瘯
docs/shortcuts.md          # 涓夌被蹇嵎鎸囦护鐨勯€愭鎼缓
docs/ai-integration.md     # 鎶婅鏃朵簨浠舵帴缁?Claude/鍏朵粬浼翠荆
```

## 涓€銆佸惎鍔ㄦ湇鍔″櫒

闇€瑕?Python 3.10+锛屼笉闇€瑕?`pip install`銆?
```bash
git clone https://github.com/Serena030/veglia-ios-bridge.git
cd veglia-ios-bridge/server
cp .env.example .env
```

鐢熸垚鍏变韩瀵嗛挜锛?
```bash
head -c 24 /dev/urandom | base64
```

缂栬緫 `.env`锛岃嚦灏戣缃細

```dotenv
VEGLIA_TOKEN=鍒氱敓鎴愮殑闀块殢鏈哄瓧绗︿覆
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=浣犵殑鍙戜欢閭
SMTP_PASSWORD=閭鐨勫簲鐢ㄤ笓鐢ㄥ瘑鐮佹垨鎺堟潈鐮?SUMMON_MAIL_TO=iPhone 閭欢鑷姩鍖栬兘澶熸敹鍒颁俊鐨勯偖绠?```

鐪熷疄 `.env` 涓嶈鎴浘銆佷笉瑕佹彁浜ゅ埌 Git锛屼篃涓嶈鎶婇偖绠辩櫥褰曞瘑鐮佺洿鎺ュ～杩涘幓銆俀Q銆丟mail
绛夐偖绠卞簲浣跨敤搴旂敤涓撶敤瀵嗙爜鎴?SMTP 鎺堟潈鐮併€?
鍚姩锛?
```bash
python3 veglia_ios.py serve
```

鏈嶅姟榛樿鍙洃鍚?`127.0.0.1:8513`銆傞€氳繃浜掕仈缃戞帴鏀?iPhone 璇锋眰鏃讹紝璇峰湪鍓嶉潰鏀?nginx/Caddy 鍜?HTTPS锛屼笉瑕佹妸瑁?HTTP 鏈嶅姟鐩存帴鏆撮湶鍒板叕缃戙€?
鍋ュ悍妫€鏌ワ細

```bash
curl http://127.0.0.1:8513/health
```

## 浜屻€佸垱寤?iPhone 鑷姩鍖?
闇€瑕佷笁绫昏嚜鍔ㄥ寲锛?
1. 鎵撳紑鐩爣 App 鏃讹紝涓婃姤 `{"app":"App 鍚?,"event":"open"}`銆?2. 鍏抽棴鐩爣 App 鏃讹紝涓婃姤 `{"app":"App 鍚?,"event":"close"}`銆?3. 鏀跺埌鍥哄畾涓婚閭欢鏃讹紝杩愯鈥滄墦寮€浼翠荆 App鈥濈殑蹇嵎鎸囦护銆?
瀹屾暣鐨勭偣鎸夋楠よ [docs/shortcuts.md](docs/shortcuts.md)銆傚厛鍙€変竴涓棤鍏崇揣瑕佺殑
娴嬭瘯 App锛涚‘璁ら摼璺彲闈犲悗鍐嶆坊鍔犲叾浠?App銆?
## 涓夈€侀€愭娴嬭瘯

鍏堟祴璇曠姸鎬佷笂鎶ワ細

```bash
curl -X POST https://浣犵殑鍩熷悕/phone/activity \
  -H 'X-Auth-Token: 浣犵殑鍏变韩瀵嗛挜' \
  -H 'Content-Type: application/json' \
  -d '{"app":"Test App","event":"open"}'

python3 veglia_ios.py status
```

鍐嶅崟鐙祴璇曞彫鍥烇細

```bash
python3 veglia_ios.py summon --reason "鍥炴潵鐪嬬湅"
```

缁堢鍑虹幇 `sent summon` 鍙〃绀洪偖浠跺彂閫佹垚鍔熴€傜瓑寰?iPhone 鏀朵俊骞惰Е鍙戣嚜鍔ㄥ寲锛涘鏋?娌℃湁鍒囧睆锛屼紭鍏堟鏌ラ偖浠朵富棰樸€佸彂浠朵汉杩囨护鏉′欢銆佲€滅珛鍗宠繍琛屸€濆拰蹇嵎鎸囦护鐨?App 閫夋嫨銆?
鏈€鍚庤繍琛屼笉鑱旂綉鐨勬祴璇曪細

```bash
python3 -m unittest test_veglia_ios.py
```

## 鍥涖€佹帴鍏?AI

璁剧疆 `VEGLIA_WATCH_HOOK` 鍚庯紝鍚屼竴娆?App 浼氳瘽杈惧埌闃堝€兼椂锛屾湇鍔″彧璋冪敤璇ョ▼搴忎竴娆★紝
骞舵妸浜嬩欢 JSON 鍐欏叆鏍囧噯杈撳叆锛?
```json
{"type":"app_watch","app":"Example App","minutes":15,"opened_at":1788432000}
```

浣犵殑 hook 璐熻矗鎶婅繖涓簨浠堕€掔粰 Claude銆丅unny 鎴栧叾浠栦即渚ｃ€備即渚ｅ喅瀹氬彫鍥炴椂鎵ц锛?
```bash
python3 /缁濆璺緞/veglia_ios.py summon --reason "涓轰粈涔堟兂璁╁ス鍥炴潵"
```

鎺ュ彛绾﹀畾銆佹帹鑽愭彁绀鸿瘝浠ュ強棰濆害鑰楀敖鏃剁殑琛屼负瑙?[docs/ai-integration.md](docs/ai-integration.md)銆傛ˉ鏈韩涓嶇粦瀹氫换浣曟ā鍨嬩緵搴斿晢銆?
## 閰嶇疆

| 鍙橀噺 | 榛樿鍊?| 鐢ㄩ€?|
|---|---:|---|
| `VEGLIA_TOKEN` | 蹇呭～ | iPhone 涓庢湇鍔″櫒鍏变韩瀵嗛挜 |
| `VEGLIA_HOST` | `127.0.0.1` | 鐩戝惉鍦板潃 |
| `VEGLIA_PORT` | `8513` | 鐩戝惉绔彛 |
| `VEGLIA_DATA_DIR` | `server/data` | 鏈湴鐘舵€佺洰褰?|
| `VEGLIA_WATCH_AFTER_MIN` | `15` | 瑙﹀彂 AI 鍒ゆ柇鐨勮繛缁娇鐢ㄥ垎閽熸暟 |
| `VEGLIA_WATCH_HOOK` | 绌?| 鎺ユ敹浜嬩欢 JSON 鐨勫彲鎵ц绋嬪簭 |
| `SMTP_HOST` / `SMTP_PORT` | 绌?/ `465` | SSL SMTP 鏈嶅姟 |
| `SMTP_USER` / `SMTP_PASSWORD` | 绌?| 鍙戜俊璐︽埛涓庡簲鐢ㄥ瘑鐮?|
| `SUMMON_MAIL_TO` | 绌?| iPhone 鎺ユ敹璐︽埛 |
| `VEGLIA_SUMMON_SUBJECT` | `[Veglia] Summon` | 閭欢鑷姩鍖栧尮閰嶄富棰?|

## 涓庡師鐗?V茅glia 鐨勫尯鍒?
| | 鍘熺増 Android | 鏈」鐩?iOS Bridge |
|---|---|---|
| 鍓嶅彴 App 鎰熺煡 | AccessibilityService 鑷姩涓婃姤 | 姣忎釜 App 鐨勫揩鎹锋寚浠よ嚜鍔ㄥ寲 |
| 鎴浘 | Android 11+ 鍚庡彴鎴浘 | 涓嶆彁渚涢潤榛樺悗鍙版埅鍥?|
| summon | App 杞鍛戒护骞舵媺璧蜂即渚?| 閭欢鑷姩鍖栨墦寮€浼翠荆 App |
| 寤惰繜 | 閫氬父鏁扮 | 閭欢閾捐矾鍙兘鍑犲崄绉?|
| 鍚庣 | Python 鏍囧噯搴?| Python 鏍囧噯搴?|

## 瀹夊叏娓呭崟

- 浣跨敤闀块殢鏈?`VEGLIA_TOKEN`锛屽苟瀹氭湡杞崲銆?- 鍙€氳繃 HTTPS 鏆撮湶 `/phone/activity`銆?- `.env`銆佺姸鎬佹暟鎹€侀偖绠卞湴鍧€鍜岀湡瀹?App 浣跨敤璁板綍姘镐笉鎻愪氦銆?- 缁欏彫鍥炶缃槑纭竟鐣岋紝骞跺憡璇夋墜鏈烘墍鏈夎€呭浣曚竴閿叧闂嚜鍔ㄥ寲銆?- 涓嶈鐢ㄥ畠鐩戣鍎跨銆佷即渚ｃ€佸憳宸ユ垨浠讳綍鏈槑纭悓鎰忕殑浜恒€?
## 鏉ユ簮銆佽鍙笌淇敼璇存槑

鏈」鐩熀浜?/ 鍙?**Evelyn & River** 鐨?[V茅glia](https://github.com/sebastianevan200-stack/veglia) 鍚彂锛屾槸闈炲畼鏂硅鐢熷疄鐜般€?
涓昏淇敼锛氫互 iOS 蹇嵎鎸囦护鍜岄偖浠惰嚜鍔ㄥ寲鏇夸唬 Android AccessibilityService锛涗笉鍖呭惈
鍚庡彴鎴浘锛涘鍔犳寔涔呭寲 App 浼氳瘽璁℃椂銆佷竴娆℃€?watch hook 鍜?SMTP summon銆?
渚濈収鍘熼」鐩綋鍓嶈鍙紝鏈」鐩互 **CC BY-NC-SA 4.0** 鍙戝竷锛氬繀椤荤讲鍚嶃€佷粎闄愰潪鍟嗕笟
浣跨敤锛岃鐢熶綔鍝侀』浠ョ浉鍚屾柟寮忓叡浜€傝瑙?[LICENSE](LICENSE) 涓?[NOTICE.md](NOTICE.md)銆?

