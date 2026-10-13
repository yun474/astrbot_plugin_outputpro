from astrbot.core.message.components import (
    At,
    Face,
    Image,
    Plain,
    Reply,
)
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
    AiocqhttpMessageEvent,
)

from ..config import PluginConfig
from ..model import OutContext, StepName, StepResult
from ..qqofficial import attach_reference, get_ref_idx, is_qqofficial_event
from .base import BaseStep


class ReplyStep(BaseStep):
    name = StepName.REPLY
    unsupported_platforms = {"dingtalk"}

    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.cfg = config.reply

    def enabled(self, ctx: OutContext) -> bool:
        if self.cfg.threshold <= 0:
            return False
        return ctx.is_llm or not self.cfg.only_llm

    async def handle(self, ctx: OutContext) -> StepResult:
        platform_name = ctx.event.get_platform_name()
        if platform_name in self.unsupported_platforms:
            return StepResult(msg=f"平台不支持智能引用，已跳过: {platform_name}")

        if not all(isinstance(x, Plain | Image | Face | At) for x in ctx.chain):
            return StepResult()

        msg_id = str(ctx.event.message_obj.message_id)
        queue = ctx.group.msg_queue
        queue_str = [str(x) for x in queue]
        if msg_id not in queue_str:
            return StepResult()
        idx = queue_str.index(msg_id)
        pushed = len(queue) - idx - 1
        if pushed < self.cfg.threshold:
            return StepResult()

        reply_id = msg_id
        if is_qqofficial_event(ctx.event):
            # QQ 官方需用 REFIDX_ 引用 ID，并在发送时写入 message_reference
            reply_id = get_ref_idx(ctx.event)
            if not reply_id:
                return StepResult(msg=f"未取到 QQ 官方消息的引用 ID，跳过引用: {msg_id}")
            if not attach_reference(ctx.event, reply_id):
                return StepResult()

        ctx.chain.insert(0, Reply(id=reply_id))
        if self.cfg.include_at and isinstance(ctx.event, AiocqhttpMessageEvent):
            ctx.chain.insert(1, At(qq=ctx.event.get_sender_id()))
            # 在 At 后添加带零宽空格包裹的空格，确保与后续内容有间距
            ctx.chain.insert(2, Plain(text="\u200b \u200b"))
        # 仅移除已引用的消息及其之前的记录，保留之后的消息用于后续引用判断
        while queue and str(queue[0]) != msg_id:
            queue.popleft()
        if queue and str(queue[0]) == msg_id:
            queue.popleft()
        # 追加 bot 插嘴标记，确保后续回复也能判断“被插嘴”
        if ctx.group.last_reply_mark_msg_id != msg_id:
            queue.append(f"__bot_reply__{msg_id}")
            ctx.group.last_reply_mark_msg_id = msg_id
        return StepResult(msg=f"已插入Reply组件, 引用消息{reply_id}")
