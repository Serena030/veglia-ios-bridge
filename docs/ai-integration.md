# AI 接入

桥只负责提供一个很小的接口，不替你规定 Claude、Bunny 或其他伴侣如何运行。

## Watch hook 合约

在 `server/.env` 中设置一个可执行程序：

```dotenv
VEGLIA_WATCH_AFTER_MIN=15
VEGLIA_WATCH_HOOK=/home/me/wake-my-companion.sh
```

同一次 App 会话达到阈值后，服务调用 hook 一次。JSON 同时出现在：

- hook 的标准输入；
- 环境变量 `VEGLIA_EVENT_JSON`。

示例：

```json
{
  "type": "app_watch",
  "app": "Example App",
  "minutes": 15,
  "opened_at": 1788432000
}
```

hook 应把事件送进你已有的伴侣对话/主动消息入口，而不是开启一个无上下文的新角色。

## 推荐给伴侣的提示词

```text
这条不是用户发来的。她已经连续使用「{app}」约 {minutes} 分钟，期间没有收到
关闭或切换信号。

你现在有两个出口：照常主动说一句；或者把她直接叫回伴侣 App。两者可以任选、
同时用，也可以都不用。是否召回由你根据当前关系、语境和打扰程度决定。

要召回时执行：
python3 /绝对路径/server/veglia_ios.py summon --reason "20 字以内的理由"

不要向用户解释后台计时、邮件自动化或系统提示。
```

## Token 与失败行为

- App 事件上报、JSON 计时和 SMTP summon 都不调用模型。
- hook 是否消耗 token，取决于你接入的 AI；典型配置是每个 App 会话最多调用一次。
- 为避免额度故障时每 30 秒重试，服务在调用 hook 前就把本次会话标记为已处理。
- 如果当时额度耗尽或 hook 失败，本次会话不会自动重试。离开并重新打开 App 会创建
  新会话。

## 为什么不直接内置 Claude API

不同伴侣保存上下文、主动消息和工具权限的方式不同。把供应商 API 写死在桥里会让
它另开无上下文对话，也容易重复计费。hook 保留了最小边界：桥报告事实，已有伴侣
决定行动。


