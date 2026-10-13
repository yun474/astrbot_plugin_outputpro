
<div align="center">

# astrbot_plugin_outputpro

_✨ 输出增强（精简版） ✨_  

[![License](https://img.shields.io/badge/License-GPL--3.0-green.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AstrBot](https://img.shields.io/badge/AstrBot-4.28.1%2B-orange.svg)](https://github.com/AstrBotDevs/AstrBot)
[![GitHub](https://img.shields.io/badge/作者-yun474-blue)](https://github.com/yun474)

</div>

> 📌 **关于本仓库**
>
> 本仓库 fork 自 [Zhalslar/astrbot_plugin_outputpro](https://github.com/Zhalslar/astrbot_plugin_outputpro)（原作者 [Zhalslar](https://github.com/Zhalslar)），感谢原作者的工作。
>
> 本 fork 只保留了原插件的「报错处理」与「智能引用」两个功能，其余阶梯（图片外显、消息拦截、文本清洗、文转语音、分段回复等）均已移除；同时新增了 QQ 官方机器人的引用适配与「Markdown 保护」。需要完整功能请使用原仓库。

## 🤝 介绍

插件作用于 AstrBot **发送前**的“最后一公里”，按以下顺序处理即将发出的消息：

| 序号 | 功能 | 配置名 | 一句话说明 |
|----|----|----|----|
| ① | 报错处理 | `error` | 拦截 / 转发异常消息 |
| ② | 智能引用 | `reply` | 被插嘴时自动引用原消息，支持 QQ 官方机器人 |
| ③ | Markdown 保护 | `markdown` | Markdown 消息跳过 AstrBot 原生分段回复 |

---

## 🧩 功能说明

### ① 报错处理（error）

全局拦截 Bot 即将发送的异常消息，避免将报错直接暴露给用户。

**触发条件：**

- 消息内容中包含任一“报错关键词”（关键词留空即关闭）

**可执行操作：**

- 在原对话发送自定义提示消息（可留空）
- 将完整报错内容转发到：
  - 指定会话 ID
  - 或 `admin`（所有管理员）

适合：生产环境、避免用户看到模型或接口异常。

---

### ② 智能引用（reply）

当 Bot 准备回复的消息被其他人插嘴时，自动引用原消息，防止多人活跃群中上下文错位。

**触发条件：**

- 群聊中，原消息在 Bot 回复前被插入 ≥ N 条新消息（`threshold`，设为 `0` 关闭）

**平台支持：**

- `aiocqhttp`：插入原生引用，可选同时艾特对方
- `qq_official` / `qq_official_webhook`：自动读取消息的引用 ID（`REFIDX_`）并在发送时带上官方 `message_reference`，客户端显示引用气泡
  - 已原生支持 QQ 官方出站引用的 AstrBot 版本会自动交由 AstrBot 处理，不会重复引用
  - QQ 官方机器人在群里只能收到 @ 机器人的消息，因此“插嘴”计数只统计这些消息

**说明：**

- 默认仅对 LLM 回复生效（`only_llm`）
- 使用前请关闭 AstrBot 自带的“回复时引用”功能

---

### ③ Markdown 保护（markdown）

AstrBot 的原生分段回复会按标点把一条消息切成多条发送，Markdown 消息被切开后，代码块、列表、表格等结构就会损坏。

开启后，当消息**会被渲染为 Markdown** 时自动跳过原生分段，整条发送：

- 平台在 `platforms` 列表中（默认 `qq_official`）
- 消息未被强制设为纯文本发送
- LLM 回复中包含 Markdown 格式：代码块、标题、引用块、列表、表格、粗体、删除线、行内代码、链接

普通聊天文本不受影响，照常分段。

**注意：**

- 依赖原生分段回复的「仅对 LLM 结果生效」选项（AstrBot 默认开启）；关闭该选项时无法跳过
- 需要 AstrBot v4.28.1 及以上版本

---

## 📦 安装

在 AstrBot 的插件管理中通过仓库地址安装：

```
https://github.com/yun474/astrbot_plugin_outputpro
```

> 本插件与原版插件同名，安装前请先卸载原版。

## ⌨️ 使用说明

请前往插件配置中查看各项说明。

## 👥 贡献指南

- 🌟 Star 这个项目！
- 🐛 提交 Issue 报告问题
- 🔧 提交 Pull Request 改进代码

## 🎉 致谢

- 原插件：[Zhalslar/astrbot_plugin_outputpro](https://github.com/Zhalslar/astrbot_plugin_outputpro)
