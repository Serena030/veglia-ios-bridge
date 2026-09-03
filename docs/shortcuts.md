# iOS 快捷指令搭建

不同 iOS 版本的按钮名称可能略有差异，但动作本身不变。先准备好：

- `https://你的域名/phone/activity`
- `.env` 中的 `VEGLIA_TOKEN`
- 要观察的测试 App
- 要被召回到前台的伴侣 App

## 1. 打开 App：发送 `open`

在“快捷指令 → 自动化”中新建个人自动化：

1. 选择“App”，选中一个测试 App，并勾选“打开时”。
2. 添加“获取 URL 内容”。
3. URL 填 `https://你的域名/phone/activity`。
4. 方法选择 `POST`，请求正文选择 `JSON`。
5. 添加文本字段 `app`，值写固定的 App 名。
6. 添加文本字段 `event`，值写 `open`。
7. 添加请求头 `X-Auth-Token`，值为 `VEGLIA_TOKEN`。
8. 选择“立即运行”，关闭“运行前询问”。

最稳妥的办法是每个受关注 App 建一条自动化，并给 `app` 写固定名字。先不要一次
勾选许多 App，否则排错时很难知道是哪条事件出了问题。

## 2. 关闭 App：发送 `close`

复制上一条自动化，然后修改：

1. 触发条件改为该 App“关闭时”。
2. JSON 的 `event` 改成 `close`。
3. 保持 URL、App 名和请求头不变。

这里的“关闭”是指离开该 App，不要求从多任务界面杀掉进程。

## 3. 收到邮件：打开伴侣 App

先创建普通快捷指令“Véglia Summon”：

1. 添加“打开 App”。
2. 选择你的伴侣 App。
3. 手动运行一次，确认它确实能切到目标 App。

再创建邮件自动化：

1. 触发器选择“电子邮件”。
2. 发件人限制为 `.env` 中的 `SMTP_USER`。
3. 主题包含 `[Veglia] Summon`；如果你改过
   `VEGLIA_SUMMON_SUBJECT`，这里必须完全一致。
4. 动作选择“运行快捷指令”，运行“Véglia Summon”。
5. 选择“立即运行”，关闭“运行前询问”。

## 4. 分段验收

打开测试 App 后，在服务器运行：

```bash
python3 veglia_ios.py status
```

应看到 `current.app` 是测试 App，并且 `seconds` 逐渐增长。离开 App 后，`current`
应变为 `null`。

然后运行：

```bash
python3 veglia_ios.py summon
```

看到 `sent summon` 后等待手机切屏。邮件可能延迟几十秒；它不是适合紧急提醒的
实时通道。

## 常见问题

### 返回 `bad_token`

快捷指令请求头与服务器 `.env` 不一致。重新复制 Token，注意不要带空格或换行。

### 状态一直计时

对应的“关闭时”自动化没有运行。检查它是否选择了同一个 App、是否为立即运行。

### 邮件收到但没有打开 App

先手动运行“Véglia Summon”。如果手动可以，问题就在邮件自动化的发件人、主题
或运行方式；如果手动也不行，重新选择“打开 App”的目标。

### `sent summon` 后很久才切屏

SMTP 接收、系统取信和快捷指令调度都有延迟。实测几十秒并不罕见。


