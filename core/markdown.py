"""Markdown 消息跳过 AstrBot 原生分段回复。

原生分段会把文本按标点切成多条发送，Markdown 消息被切开后代码块、列表、
表格等结构会损坏。原生分段在「仅对 LLM 结果生效」时通过
result.is_model_result() 判断是否处理，这里仅对当前这条结果覆盖该判断，
使其按普通消息整条发送，不影响 is_llm_result() 及其他消息。
"""

from __future__ import annotations

import re

from astrbot.api import logger
from astrbot.core.message.components import Plain
from astrbot.core.platform.astr_message_event import AstrMessageEvent

from .config import MarkdownConfig

MARKDOWN_RE = re.compile(
    r"```"  # 代码块
    r"|^ {0,3}#{1,6}\s+\S"  # 标题
    r"|^ {0,3}>"  # 引用块
    r"|^\s*(?:[-*+]|\d+\.)\s+\S"  # 列表
    r"|^\s*\|.+\|\s*$"  # 表格
    r"|\*\*[^*\n]+\*\*"  # 粗体
    r"|~~[^~\n]+~~"  # 删除线
    r"|`[^`\n]+`"  # 行内代码
    r"|\[[^\]\n]+\]\([^)\s]+\)",  # 链接
    re.MULTILINE,
)


def has_markdown(text: str) -> bool:
    return bool(MARKDOWN_RE.search(text))


class MarkdownGuard:
    def __init__(self, config: MarkdownConfig):
        self.cfg = config

    def handle(self, event: AstrMessageEvent) -> None:
        if not self.cfg.skip_native_split:
            return
        if event.get_platform_name() not in self.cfg.platforms:
            return

        result = event.get_result()
        if not result or not result.chain:
            return
        # 明确要求纯文本发送时不会渲染为 Markdown
        if result.use_markdown_ is False:
            return
        if not hasattr(result, "is_model_result"):
            logger.debug("[OutputPro] 当前 AstrBot 版本不支持跳过原生分段")
            return
        if not result.is_model_result():
            return

        text = "".join(c.text for c in result.chain if isinstance(c, Plain))
        if not has_markdown(text):
            return

        result.is_model_result = lambda: False
        logger.debug("[OutputPro] 检测到 Markdown 消息，已跳过原生分段回复")
