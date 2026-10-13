from astrbot.api.event import filter
from astrbot.api.star import Context, Star
from astrbot.core import AstrBotConfig
from astrbot.core.platform.astr_message_event import AstrMessageEvent

from .core.config import PluginConfig
from .core.markdown import MarkdownGuard
from .core.model import OutContext, StateManager
from .core.pipeline import Pipeline


class OutputPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.cfg = PluginConfig(config, context)
        self.pipeline = Pipeline(self.cfg)
        self.md_guard = MarkdownGuard(self.cfg.markdown)

    async def initialize(self):
        await self.pipeline.initialize()

    async def terminate(self):
        await self.pipeline.terminate()

    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE, priority=1000)
    async def on_message(self, event: AstrMessageEvent):
        """收到群消息时，记录消息用于智能引用判断"""
        if self.cfg.reply.threshold <= 0:
            return
        if event.get_sender_id() == event.get_self_id():
            return
        g = StateManager.get_group(event.get_group_id())
        g.msg_queue.append(event.message_obj.message_id)

    @filter.on_decorating_result(priority=15)
    async def on_decorating_result(self, event: AstrMessageEvent):
        """发送消息前"""
        result = event.get_result()
        if not result or not result.chain:
            return

        ctx = OutContext(
            event=event,
            chain=result.chain,
            is_llm=result.is_llm_result(),
            plain=result.get_plain_text(),
            gid=event.get_group_id(),
            uid=event.get_sender_id(),
            bid=event.get_self_id(),
            group=StateManager.get_group(event.get_group_id()),
            timestamp=event.message_obj.timestamp,
        )

        await self.pipeline.run(ctx)

    @filter.on_decorating_result(priority=-100)
    async def skip_native_split_for_markdown(self, event: AstrMessageEvent):
        """发送前最后检查：Markdown 消息跳过原生分段（低优先级，在其他插件处理完后执行）"""
        self.md_guard.handle(event)
