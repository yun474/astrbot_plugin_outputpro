"""QQ 官方机器人（qq_official / qq_official_webhook）引用回复适配。

QQ 官方接口的引用依赖 payload 中的 message_reference.message_id，其取值为
用户消息事件 message_scene.ext 中的 msg_idx（REFIDX_...），而不是消息本身的
id（ROBOT1.0_...）。旧版 AstrBot 的适配器会直接丢弃 Reply 组件，这里通过包装
单个事件实例的发送方法补上该字段；新版 AstrBot 已原生支持时自动让位。
"""

from __future__ import annotations

from typing import Any

from astrbot.api import logger
from astrbot.core.platform.sources.qqofficial.qqofficial_message_event import (
    QQOfficialMessageEvent,
)

_SEND_METHOD = "_send_with_markdown_fallback"


def is_qqofficial_event(event: Any) -> bool:
    return isinstance(event, QQOfficialMessageEvent)


def get_ref_idx(event: QQOfficialMessageEvent) -> str:
    """取用户消息自身的引用 ID（REFIDX_...），取不到时返回空串"""
    raw = getattr(event.message_obj.raw_message, "raw_data", None)
    if not isinstance(raw, dict):
        return ""
    scene = raw.get("message_scene")
    if not isinstance(scene, dict):
        return ""
    for item in scene.get("ext") or []:
        text = str(item)
        if text.startswith("msg_idx="):
            return text[len("msg_idx=") :].strip()
    return ""


def attach_reference(event: QQOfficialMessageEvent, ref_idx: str) -> bool:
    """让该事件接下来的第一次发送携带引用。

    仅包装当前事件实例，不影响其他消息；若 AstrBot 已自行填充
    message_reference（新版原生支持），则不再覆盖。
    """
    origin = getattr(type(event), _SEND_METHOD, None)
    if origin is None:
        logger.warning("[OutputPro] 当前 AstrBot 版本的 QQ 官方适配器结构不兼容，跳过引用")
        return False

    used = False

    async def send_with_reference(send_func, payload: dict, *args, **kwargs):
        nonlocal used
        if not used:
            used = True
            if not payload.get("message_reference"):
                payload["message_reference"] = {"message_id": ref_idx}
        return await origin(send_func, payload, *args, **kwargs)

    setattr(event, _SEND_METHOD, send_with_reference)
    return True
