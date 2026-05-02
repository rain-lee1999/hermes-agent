"""Tests for the bark_macos_notify plugin."""
from __future__ import annotations

import importlib
from pathlib import Path

import pytest
import yaml

from hermes_cli.plugins import PluginManager

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_DIR = REPO_ROOT / "plugins" / "bark_macos_notify"


def _module():
    return importlib.import_module("plugins.bark_macos_notify")


class TestManifest:
    def test_plugin_directory_exists(self):
        assert PLUGIN_DIR.is_dir()
        assert (PLUGIN_DIR / "plugin.yaml").exists()
        assert (PLUGIN_DIR / "__init__.py").exists()

    def test_manifest_fields(self):
        data = yaml.safe_load((PLUGIN_DIR / "plugin.yaml").read_text(encoding="utf-8"))
        assert data["name"] == "bark_macos_notify"
        assert data["version"] == "1.1.0"
        assert data["default_enabled"] is True
        assert data["provides_hooks"] == [
            "pre_tool_call",
            "post_llm_call",
            "on_session_finalize",
            "on_session_reset",
        ]


class TestModuleBehavior:
    def test_constants_and_cleaning(self):
        mod = _module()
        assert mod.DEFAULT_TITLE == PLUGIN_DIR.name
        assert mod.REQUIRED_INPUT_MESSAGE == "Hermes needs your input"
        assert mod._clean("  hello\r\nworld  ") == "hello world"
        cleaned = mod._clean("x" * 400)
        assert cleaned.endswith("…")
        assert len(cleaned) == mod.MAX_BODY

    def test_register_hooks(self):
        mod = _module()
        calls = []

        class Ctx:
            def register_hook(self, name, fn):
                calls.append((name, fn))

        mod.register(Ctx())
        assert [name for name, _ in calls] == [
            "pre_tool_call",
            "post_llm_call",
            "on_session_finalize",
            "on_session_reset",
        ]
        assert all(callable(fn) for _, fn in calls)

    def test_filters_cover_required_input_progress_and_background_turns(self, monkeypatch):
        mod = _module()

        assert mod._should_send_required_input_notification(
            {"tool_name": " clarify ", "session_id": "root"}
        )
        assert not mod._should_send_required_input_notification(
            {"tool_name": "search", "session_id": "root"}
        )

        assert mod._should_send_task_complete(
            {"assistant_response": "All done.", "session_id": "root"}
        )
        assert not mod._should_send_task_complete(
            {"assistant_response": "Could you help?", "session_id": "root"}
        )
        assert not mod._should_send_task_complete(
            {"assistant_response": "Still running, monitoring.", "session_id": "root"}
        )
        assert not mod._should_send_task_complete(
            {
                "assistant_response": "All done.",
                "session_id": "root",
                "user_message": "[system: background process matched watch pattern completed]",
            }
        )

        monkeypatch.setenv("HERMES_NOTIFY_WAITING", "1")
        assert mod._should_send_waiting(
            {"assistant_response": "Still working", "session_id": "root"}
        )
        assert not mod._should_send_waiting(
            {
                "assistant_response": "Still working",
                "session_id": "root",
                "user_message": "[system: background process completed]",
            }
        )

    def test_send_bark_builds_expected_curl_command(self, monkeypatch):
        mod = _module()
        calls = []
        monkeypatch.setenv("BARK_URL", "https://api.day.app/key")
        monkeypatch.setenv("HERMES_NOTIFY_GROUP", "Hermes")
        monkeypatch.setenv("HERMES_NOTIFY_LEVEL", "active")
        monkeypatch.setenv("HERMES_NOTIFY_BARK_SOUND", "bell")
        monkeypatch.setattr(
            mod.subprocess,
            "run",
            lambda *args, **kwargs: calls.append((args, kwargs)),
        )

        mod._send_bark("Title", "Body text", "task_complete")

        assert len(calls) == 1
        args, kwargs = calls[0]
        assert args[0] == [
            "curl",
            "-fsS",
            "--max-time",
            "8",
            (
                "https://api.day.app/key/Title/Body%20text"
                "?group=Hermes&level=active&url=hermes%3A%2F%2Ftask_complete"
                "&sound=bell"
            ),
        ]
        assert kwargs["check"] is False
        assert kwargs["timeout"] == 10

    def test_send_macos_builds_expected_osascript_command(self, monkeypatch):
        mod = _module()
        calls = []
        monkeypatch.setattr(
            mod.subprocess,
            "run",
            lambda *args, **kwargs: calls.append((args, kwargs)),
        )

        mod._send_macos("Title", "Body text", "Sub")

        assert len(calls) == 1
        args, kwargs = calls[0]
        assert args[0] == [
            "osascript",
            "-e",
            'display notification "Body text" with title "Title" subtitle "Sub"',
        ]
        assert kwargs["check"] is False
        assert kwargs["timeout"] == 5

    @pytest.mark.parametrize(
        "hook_name,flag_name,event_key,subtitle",
        [
            (
                "on_session_finalize",
                "HERMES_NOTIFY_FINALIZE",
                "finalize",
                "cli · finalize",
            ),
            (
                "on_session_reset",
                "HERMES_NOTIFY_RESET",
                "reset",
                "cli · reset",
            ),
        ],
    )
    def test_session_boundary_hooks_emit_notifications(
        self, monkeypatch, hook_name, flag_name, event_key, subtitle
    ):
        mod = _module()
        calls = []
        monkeypatch.setenv(flag_name, "1")
        monkeypatch.setattr(
            mod,
            "_notify",
            lambda *args, **kwargs: calls.append((args, kwargs)),
        )

        getattr(mod, hook_name)(session_id="abc", platform="cli")

        assert calls == [
            ((mod.DEFAULT_TITLE, "session=abc", event_key), {"subtitle": subtitle})
        ]

    @pytest.mark.parametrize(
        "helper_name,event_key,subtitle",
        [
            ("_should_send_task_complete", "task_complete", "cli · task complete"),
            ("_should_send_waiting", "waiting", "cli · 本轮回复完成"),
        ],
    )
    def test_on_post_llm_call_routes_notifications(
        self, monkeypatch, helper_name, event_key, subtitle
    ):
        mod = _module()
        calls = []
        monkeypatch.setattr(mod, "_should_send_task_complete", lambda kwargs: helper_name == "_should_send_task_complete")
        monkeypatch.setattr(mod, "_should_send_waiting", lambda kwargs: helper_name == "_should_send_waiting")
        monkeypatch.setattr(
            mod,
            "_notify",
            lambda *args, **kwargs: calls.append((args, kwargs)),
        )

        mod.on_post_llm_call(assistant_response="Done", platform="cli")

        assert calls == [
            ((mod.DEFAULT_TITLE, "Done", event_key), {"subtitle": subtitle})
        ]

    def test_on_pre_tool_call_emits_required_input_notification(self, monkeypatch):
        mod = _module()
        calls = []
        monkeypatch.setattr(
            mod,
            "_should_send_required_input_notification",
            lambda kwargs: True,
        )
        monkeypatch.setattr(
            mod,
            "_notify",
            lambda *args, **kwargs: calls.append((args, kwargs)),
        )

        mod.on_pre_tool_call(tool_name="clarify", session_id="root")

        assert calls == [
            ((mod.DEFAULT_TITLE, mod.REQUIRED_INPUT_MESSAGE, "needs_input"), {})
        ]


class TestPluginDiscoveryIntegration:
    def test_default_enabled_plugin_loads_without_allowlist(self, tmp_path, monkeypatch):
        hermes_home = tmp_path / "hermes_home"
        hermes_home.mkdir()
        (hermes_home / "config.yaml").write_text(
            "plugins:\n  enabled: []\n",
            encoding="utf-8",
        )
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))

        calls = []

        mgr = PluginManager()
        mgr.discover_and_load(force=True)

        listing = mgr.list_plugins()
        bark = next(item for item in listing if item["name"] == "bark_macos_notify")
        assert bark["enabled"] is True

        mod = mgr._plugins["bark_macos_notify"].module
        assert mod is not None
        monkeypatch.setattr(mod, "_should_send_task_complete", lambda kwargs: True)
        monkeypatch.setattr(
            mod,
            "_notify",
            lambda *args, **kwargs: calls.append((args, kwargs)),
        )

        mgr.invoke_hook(
            "post_llm_call",
            assistant_response="Done",
            platform="cli",
            session_id="session-1",
            user_message="hello",
        )

        assert calls == [
            ((mod.DEFAULT_TITLE, "Done", "task_complete"), {"subtitle": "cli · task complete"})
        ]
