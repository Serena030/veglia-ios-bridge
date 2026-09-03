# Véglia iOS Bridge（非官方）

> An unofficial iOS Shortcuts bridge inspired by [Véglia](https://github.com/sebastianevan200-stack/veglia).

用 **iOS 快捷指令 + 邮件自动化 + 自托管 Python 服务**，把 iPhone 上的 App
使用状态交给你的 AI 伴侣，并允许它在你停留太久时把伴侣 App 叫回前台。

这不是原作者维护的官方 iOS 版本，也不是 Android 版的等价移植。iOS 不允许普通
第三方应用像 Android AccessibilityService 那样在后台静默截图；本项目只实现
文字状态上报和用户明确开启的 `summon`。

## 先说清楚：同意，不是监视

这个桥只应该安装在**手机所有者本人知情并主动配置**的设备上。`summon` 会打断
当前操作，所以它必须是一项可以随时关闭的明确授权，而不是惩罚或控制手段。

默认流程不读取截图：

- App 打开/关闭：只上传 App 名、事件类型和服务器时间。
- 后台计时：只读本地 JSON，不调用模型。
- `summon`：只发一封固定主题邮件，不调用模型。
- 只有“让 AI 决定要不要召回”这一步会产生一次模型调用。

## 它怎样工作

```text
iPhone App 自动化
  → POST /phone/activity
  → VPS 记录当前 App 和开始时间
  → 满 15 分钟触发一次 VEGLIA_WATCH_HOOK
  → 你的 AI：说一句 / summon / 两者都做 / 暂不打扰
  → python3 veglia_ios.py summon
  → 邮件自动化运行「打开 App」快捷指令
```

邮件推送并非实时协议，真机上出现几十秒延迟是正常现象。

## 目录

```text
server/veglia_ios.py       # 零依赖服务、状态 CLI、summon 邮件
server/.env.example        # 配置模板
server/test_veglia_ios.py  # 不联网的单元测试
docs/shortcuts.md          # 三类快捷指令的逐步搭建
docs/ai-integration.md     # 把计时事件接给 Claude/其他伴侣
```

## 一、启动服务器

需要 Python 3.10+，不需要 `pip install`。

```bash
git clone https://github.com/Serena030/veglia-ios-bridge.git
cd veglia-ios-bridge/server
cp .env.example .env
```

生成共享密钥：

```bash
head -c 24 /dev/urandom | base64
```

编辑 `.env`，至少设置：

```dotenv
VEGLIA_TOKEN=刚生成的长随机字符串
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=你的发件邮箱
SMTP_PASSWORD=邮箱的应用专用密码或授权码
SUMMON_MAIL_TO=iPhone 邮件自动化能够收到信的邮箱
```

真实 `.env` 不要截图、不要提交到 Git，也不要把邮箱登录密码直接填进去。QQ、Gmail
等邮箱应使用应用专用密码或 SMTP 授权码。

启动：

```bash
python3 veglia_ios.py serve
```

服务默认只监听 `127.0.0.1:8513`。通过互联网接收 iPhone 请求时，请在前面放
nginx/Caddy 和 HTTPS，不要把裸 HTTP 服务直接暴露到公网。

健康检查：

```bash
curl http://127.0.0.1:8513/health
```

## 二、创建 iPhone 自动化

需要三类自动化：

1. 打开目标 App 时，上报 `{"app":"App 名","event":"open"}`。
2. 关闭目标 App 时，上报 `{"app":"App 名","event":"close"}`。
3. 收到固定主题邮件时，运行“打开伴侣 App”的快捷指令。

完整的点按步骤见 [docs/shortcuts.md](docs/shortcuts.md)。先只选一个无关紧要的
测试 App；确认链路可靠后再添加其他 App。

## 三、逐段测试

先测试状态上报：

```bash
curl -X POST https://你的域名/phone/activity \
  -H 'X-Auth-Token: 你的共享密钥' \
  -H 'Content-Type: application/json' \
  -d '{"app":"Test App","event":"open"}'

python3 veglia_ios.py status
```

再单独测试召回：

```bash
python3 veglia_ios.py summon --reason "回来看看"
```

终端出现 `sent summon` 只表示邮件发送成功。等待 iPhone 收信并触发自动化；如果
没有切屏，优先检查邮件主题、发件人过滤条件、“立即运行”和快捷指令的 App 选择。

最后运行不联网的测试：

```bash
python3 -m unittest test_veglia_ios.py
```

## 四、接入 AI

设置 `VEGLIA_WATCH_HOOK` 后，同一次 App 会话达到阈值时，服务只调用该程序一次，
并把事件 JSON 写入标准输入：

```json
{"type":"app_watch","app":"Example App","minutes":15,"opened_at":1788432000}
```

你的 hook 负责把这个事件递给 Claude、Bunny 或其他伴侣。伴侣决定召回时执行：

```bash
python3 /绝对路径/veglia_ios.py summon --reason "为什么想让她回来"
```

接口约定、推荐提示词以及额度耗尽时的行为见
[docs/ai-integration.md](docs/ai-integration.md)。桥本身不绑定任何模型供应商。

## 配置

| 变量 | 默认值 | 用途 |
|---|---:|---|
| `VEGLIA_TOKEN` | 必填 | iPhone 与服务器共享密钥 |
| `VEGLIA_HOST` | `127.0.0.1` | 监听地址 |
| `VEGLIA_PORT` | `8513` | 监听端口 |
| `VEGLIA_DATA_DIR` | `server/data` | 本地状态目录 |
| `VEGLIA_WATCH_AFTER_MIN` | `15` | 触发 AI 判断的连续使用分钟数 |
| `VEGLIA_WATCH_HOOK` | 空 | 接收事件 JSON 的可执行程序 |
| `SMTP_HOST` / `SMTP_PORT` | 空 / `465` | SSL SMTP 服务 |
| `SMTP_USER` / `SMTP_PASSWORD` | 空 | 发信账户与应用密码 |
| `SUMMON_MAIL_TO` | 空 | iPhone 接收账户 |
| `VEGLIA_SUMMON_SUBJECT` | `[Veglia] Summon` | 邮件自动化匹配主题 |

## 与原版 Véglia 的区别

| | 原版 Android | 本项目 iOS Bridge |
|---|---|---|
| 前台 App 感知 | AccessibilityService 自动上报 | 每个 App 的快捷指令自动化 |
| 截图 | Android 11+ 后台截图 | 不提供静默后台截图 |
| summon | App 轮询命令并拉起伴侣 | 邮件自动化打开伴侣 App |
| 延迟 | 通常数秒 | 邮件链路可能几十秒 |
| 后端 | Python 标准库 | Python 标准库 |

## 安全清单

- 使用长随机 `VEGLIA_TOKEN`，并定期轮换。
- 只通过 HTTPS 暴露 `/phone/activity`。
- `.env`、状态数据、邮箱地址和真实 App 使用记录永不提交。
- 给召回设置明确边界，并告诉手机所有者如何一键关闭自动化。
- 不要用它监视儿童、伴侣、员工或任何未明确同意的人。

## 来源、许可与修改说明

本项目基于 / 受 **Evelyn & River** 的
[Véglia](https://github.com/sebastianevan200-stack/veglia) 启发，是非官方衍生实现。

主要修改：以 iOS 快捷指令和邮件自动化替代 Android AccessibilityService；不包含
后台截图；增加持久化 App 会话计时、一次性 watch hook 和 SMTP summon。

依照原项目当前许可，本项目以 **CC BY-NC-SA 4.0** 发布：必须署名、仅限非商业
使用，衍生作品须以相同方式共享。详见 [LICENSE](LICENSE) 与 [NOTICE.md](NOTICE.md)。


