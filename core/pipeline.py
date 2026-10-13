from __future__ import annotations

from astrbot.api import logger

from .config import PluginConfig
from .model import OutContext
from .step import BaseStep, ErrorStep, ReplyStep


class Pipeline:
    """
    输出管道：

    - 按固定顺序构建 step 实例（报错处理 → 智能引用）
    - 统一 initialize / terminate
    - 对外唯一接口：run
    """

    STEP_CLASSES: list[type[BaseStep]] = [ErrorStep, ReplyStep]

    def __init__(self, config: PluginConfig):
        self.plugin_config = config
        self._steps: list[BaseStep] = [cls(config) for cls in self.STEP_CLASSES]

    # =================== Lifecycle =======================

    async def initialize(self) -> None:
        """初始化所有步骤"""
        for step in self._steps:
            await step.initialize()

    async def terminate(self) -> None:
        """终止所有步骤"""
        for step in self._steps:
            await step.terminate()

    # ==================== run =====================

    async def run(self, ctx: OutContext) -> bool:
        """
        运行 pipeline
        """
        for step in self._steps:
            if not step.enabled(ctx):
                continue

            result = await step.handle(ctx)
            if result.msg:
                if result.ok:
                    logger.debug(result.msg)
                else:
                    logger.warning(result.msg)

            if result.abort:
                return False

        return True
