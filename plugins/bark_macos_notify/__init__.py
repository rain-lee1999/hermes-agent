"""Bark and macOS notification plugin for Hermes."""

from __future__ import annotations

import json
import logging
import os
import subprocess
import urllib.parse
from functools import lru_cache

logger = logging.getLogger(__name__)

TRUTHY = {"1", "true", "yes", "on"}
DEFAULT_TITLE = os.path.basename(os.path.dirname(__file__)) or "Hermes"
MAX_BODY = 220
REQUIRED_INPUT_MESSAGE = "Hermes needs your input"
_REQUIRED_INPUT_TOKENS = (
    "请提供",
    "请确认",
    "请上传",
    "请补充",
    "请选择",
    "请粘贴",
    "请发送",
    "告诉我",
    "please provide",
    "please confirm",
    "please upload",
    "please choose",
    "please share",
    "could you",
    "can you",
)
_PROGRESS_TOKENS = (
    "继续等待",
    "继续处理",
    "继续运行",
    "继续监控",
    "继续观察",
    "稍后",
    "还在",
    "仍在",
    "进行中",
    "未完成",
    "没完成",
    "处理中",
    "等待其余",
    "waiting for",
    "still running",
    "still working",
    "continuing",
    "in progress",
    "ongoing",
    "monitoring",
    "not finished",
    "not done yet",
)


def _flag(name: str, default: bool = True) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in TRUTHY


def _clean(text: str | None, limit: int = MAX_BODY) -> str:
    text = (text or "").strip().replace("\r", " ").replace("\n", " ")
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _send_bark(title: str, body: str, event_key: str) -> None:
    if not _flag("HERMES_NOTIFY_BARK", True):
        return
    base = (os.getenv("BARK_URL") or "").strip()
    if not base:
        return
    group = urllib.parse.quote(os.getenv("HERMES_NOTIFY_GROUP", DEFAULT_TITLE), safe="")
    level = urllib.parse.quote(os.getenv("HERMES_NOTIFY_LEVEL", "active"), safe="")
    sound = urllib.parse.quote(os.getenv("HERMES_NOTIFY_BARK_SOUND", ""), safe="")
    url = (
        f"{base.rstrip('/')}"
        f"/{urllib.parse.quote(title, safe='')}"
        f"/{urllib.parse.quote(body, safe='')}"
        f"?group={group}&level={level}&url={urllib.parse.quote('hermes://' + event_key, safe='')}"
    )
    if sound:
        url += f"&sound={sound}"
    try:
        subprocess.run(
            ["curl", "-fsS", "--max-time", "8", url],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
    except Exception as exc:  # pragma: no cover - defensive logging path
        logger.warning("Bark notification failed: %s", exc)


def _apple_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _send_macos(title: str, body: str, subtitle: str = "") -> None:
    if not _flag("HERMES_NOTIFY_MACOS", True):
        return
    script = (
        "display notification " + _apple_string(body)
        + " with title " + _apple_string(title)
        + (" subtitle " + _apple_string(subtitle) if subtitle else "")
    )
    try:
        subprocess.run(["osascript", "-e", script], check=False, timeout=5)
    except Exception as exc:  # pragma: no cover - defensive logging path
        logger.warning("macOS notification failed: %s", exc)


def _notify(title: str, body: str, event_key: str, subtitle: str = "") -> None:
    body = _clean(body)
    if not body:
        return
    _send_bark(title, body, event_key)
    _send_macos(title, body, subtitle)


def _platform(kwargs: dict) -> str:
    return (kwargs.get("platform") or "cli").strip() or "cli"


@lru_cache(maxsize=256)
def _is_child_session(session_id: str) -> bool:
    if not session_id:
        return False
    try:
        from hermes_state import SessionDB

        session = SessionDB().get_session(session_id)
        return bool(session and session.get("parent_session_id"))
    except Exception as exc:  # pragma: no cover - DB lookup is best-effort
        logger.debug("Could not resolve session lineage for notifications: %s", exc)
        return False


def _should_notify(kwargs: dict) -> bool:
    session_id = (kwargs.get("session_id") or "").strip()
    if not session_id:
        return True
    return not _is_child_session(session_id)


def _normalized_user_message(kwargs: dict) -> str:
    user_message = kwargs.get("user_message")
    if not isinstance(user_message, str):
        return ""
    return " ".join(user_message.split()).lower()


def _is_background_system_turn(kwargs: dict) -> bool:
    normalized = _normalized_user_message(kwargs)
    if "[system:" not in normalized:
        return False
    if "background process" not in normalized:
        return False
    return "matched watch pattern" in normalized or "completed" in normalized


def _needs_required_input(response: str) -> bool:
    normalized = response.lower()
    if normalized.endswith("?") or normalized.endswith("？"):
        return True
    return any(token in normalized for token in _REQUIRED_INPUT_TOKENS)


def _is_progress_response(response: str) -> bool:
    normalized = response.lower()
    return any(token in normalized for token in _PROGRESS_TOKENS)


def _should_send_required_input_notification(kwargs: dict) -> bool:
    if not _should_notify(kwargs):
        return False
    tool_name = (kwargs.get("tool_name") or "").strip()
    return tool_name == "clarify"


def _should_send_task_complete(kwargs: dict) -> bool:
    if not _should_notify(kwargs):
        return False
    if _is_background_system_turn(kwargs):
        return False
    if not _flag("HERMES_NOTIFY_TASK_COMPLETE", True):
        return False
    response = _clean(kwargs.get("assistant_response"))
    if not response:
        return False
    if _needs_required_input(response):
        return False
    if _is_progress_response(response):
        return False
    return True


def _should_send_waiting(kwargs: dict) -> bool:
    if not _should_notify(kwargs):
        return False
    if _is_background_system_turn(kwargs):
        return False
    if not _flag("HERMES_NOTIFY_WAITING", False):
        return False
    response = _clean(kwargs.get("assistant_response"))
    if not response:
        return False
    return True


def on_pre_tool_call(**kwargs):
    if not _should_send_required_input_notification(kwargs):
        return
    _notify(DEFAULT_TITLE, REQUIRED_INPUT_MESSAGE, "needs_input")


def on_post_llm_call(**kwargs):
    assistant_response = _clean(kwargs.get("assistant_response") or "")
    if not assistant_response:
        return
    platform = _platform(kwargs)

    if _should_send_task_complete(kwargs):
        _notify(
            DEFAULT_TITLE,
            assistant_response,
            "task_complete",
            subtitle=f"{platform} · task complete",
        )
        return

    if _should_send_waiting(kwargs):
        _notify(
            DEFAULT_TITLE,
            assistant_response,
            "waiting",
            subtitle=f"{platform} · 本轮回复完成",
        )


def on_session_finalize(**kwargs):
    if not _should_notify(kwargs):
        return
    if not _flag("HERMES_NOTIFY_FINALIZE", False):
        return
    platform = _platform(kwargs)
    session_id = kwargs.get("session_id") or "unknown"
    _notify(
        DEFAULT_TITLE,
        f"session={session_id}",
        "finalize",
        subtitle=f"{platform} · finalize",
    )


def on_session_reset(**kwargs):
    if not _should_notify(kwargs):
        return
    if not _flag("HERMES_NOTIFY_RESET", False):
        return
    platform = _platform(kwargs)
    session_id = kwargs.get("session_id") or "unknown"
    _notify(
        DEFAULT_TITLE,
        f"session={session_id}",
        "reset",
        subtitle=f"{platform} · reset",
    )


def register(ctx):
    ctx.register_hook("pre_tool_call", on_pre_tool_call)
    ctx.register_hook("post_llm_call", on_post_llm_call)
    ctx.register_hook("on_session_finalize", on_session_finalize)
    ctx.register_hook("on_session_reset", on_session_reset)
