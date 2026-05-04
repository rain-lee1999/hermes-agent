from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_sync_module():
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "reorder_codex_by_menubar_quota.py"
    spec = importlib.util.spec_from_file_location("reorder_codex_by_menubar_quota", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def row(row_id: str, display_name: str, *, weekly: int = 50, five_hour: int = 100) -> dict:
    return {
        "id": row_id,
        "displayName": display_name,
        "planType": "plus",
        "usageState": "ok",
        "weeklyRemainingPercent": weekly,
        "weeklyResetAt": 100,
        "fiveHourRemainingPercent": five_hour,
        "quotaWeight": 20,
    }


class _PrimeResponse:
    status_code = 200
    text = 'event: response.created\ndata: {"type":"response.created","response":{"id":"resp_prime_123"}}\n\n'

    def raise_for_status(self):
        return None

    def json(self):
        raise AssertionError("streaming Codex response is not plain JSON")


class _PrimeClient:
    def __init__(self):
        self.requests = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, url, headers=None, json=None):
        self.requests.append({"url": url, "headers": headers or {}, "json": json or {}})
        return _PrimeResponse()


def entry(row_id: str, label: str, access: str, refresh: str, priority: int) -> dict:
    return {
        "label": label,
        "provider": "openai-codex",
        "source": f"manual:codex-file:{row_id}",
        "imported_from": row_id,
        "access_token": access,
        "refresh_token": refresh,
        "priority": priority,
    }


def test_build_ranking_preserves_menubar_last_menu_rows_order():
    module = load_sync_module()
    rows = [
        row("top", "z-top", weekly=10),
        row("would-sort-first", "a-better", weekly=99),
    ]

    ranked, lookup = module.build_ranking(rows)

    assert [item["id"] for item in ranked] == ["top", "would-sort-first"]
    assert list(lookup) == ["top", "would-sort-first"]


def test_reorder_entries_uses_menubar_file_order_not_local_resort():
    module = load_sync_module()
    rows = [
        row("top", "z-top", weekly=10),
        row("would-sort-first", "a-better", weekly=99),
    ]
    _ranked, lookup = module.build_ranking(rows)
    entries = [
        entry("would-sort-first", "better", "better_access", "better_refresh", 0),
        entry("top", "top", "top_access", "top_refresh", 1),
    ]

    reordered, _movement, ranked_matches = module.reorder_entries(entries, lookup, current_row=None)

    assert [item["imported_from"] for item in reordered] == ["top", "would-sort-first"]
    assert [item["priority"] for item in reordered] == [0, 1]
    assert [item["id"] for item in ranked_matches] == ["top", "would-sort-first"]


def test_main_apply_updates_hermes_auth_from_first_menubar_row(tmp_path, monkeypatch, capsys):
    module = load_sync_module()
    rows_path = tmp_path / "last-menu-rows.json"
    auth_path = tmp_path / "auth.json"
    codex_home = tmp_path / ".codex"
    backup_dir = tmp_path / "backups"
    codex_home.mkdir()

    rows_path.write_text(
        json.dumps([
            row("top", "z-top", weekly=10),
            row("would-sort-first", "a-better", weekly=99),
        ]),
        encoding="utf-8",
    )
    for row_id, access, refresh in [
        ("top", "top_access", "top_refresh"),
        ("would-sort-first", "better_access", "better_refresh"),
    ]:
        (codex_home / row_id).write_text(
            json.dumps({"tokens": {"access_token": access, "refresh_token": refresh}}),
            encoding="utf-8",
        )
    auth_path.write_text(
        json.dumps(
            {
                "version": 1,
                "providers": {
                    "openai-codex": {
                        "auth_mode": "chatgpt",
                        "tokens": {
                            "access_token": "old_access",
                            "refresh_token": "old_refresh",
                        },
                    }
                },
                "credential_pool": {
                    "openai-codex": [
                        entry("would-sort-first", "better", "better_access", "better_refresh", 0),
                        entry("top", "top", "top_access", "top_refresh", 1),
                    ]
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(module, "APP_ROWS_PATH", rows_path)
    monkeypatch.setattr(module, "HERMES_AUTH_PATH", auth_path)
    monkeypatch.setattr(module, "CODEX_HOME", codex_home)
    monkeypatch.setattr(module, "BACKUP_DIR", backup_dir)
    monkeypatch.setattr(sys, "argv", ["reorder_codex_by_menubar_quota.py", "--apply", "--quiet"])

    assert module.main() == 0
    payload = json.loads(capsys.readouterr().out)
    updated = json.loads(auth_path.read_text(encoding="utf-8"))

    pool = updated["credential_pool"]["openai-codex"]
    assert payload["applied"] is True
    assert payload["changed"] is True
    assert payload["provider_synced"] is True
    assert Path(payload["backup"]).exists()
    assert [item["imported_from"] for item in pool] == ["top", "would-sort-first"]
    assert [item["priority"] for item in pool] == [0, 1]
    assert updated["providers"]["openai-codex"]["tokens"]["access_token"] == "top_access"
    assert updated["providers"]["openai-codex"]["tokens"]["refresh_token"] == "top_refresh"


def test_five_hour_prime_candidates_require_full_quota_and_full_reset_window():
    module = load_sync_module()
    now = 1_000_000
    stale_full = row("auth.full.json", "full", five_hour=100)
    stale_full["fiveHourResetAt"] = now + module.FIVE_HOUR_WINDOW_SECONDS
    partly_used = row("auth.used.json", "used", five_hour=99)
    partly_used["fiveHourResetAt"] = now + module.FIVE_HOUR_WINDOW_SECONDS
    short_reset = row("auth.short.json", "short", five_hour=100)
    short_reset["fiveHourResetAt"] = now + 120

    candidates = module.five_hour_prime_candidates([stale_full, partly_used, short_reset], now_ts=now)

    assert [item["id"] for item in candidates] == ["auth.full.json"]


def test_prime_full_five_hour_rows_respects_per_account_cooldown(tmp_path, monkeypatch):
    module = load_sync_module()
    row_id = "auth.full.json"
    target_row = row(row_id, "full", five_hour=100)
    target_row["fiveHourResetAt"] = 1_000_000 + module.FIVE_HOUR_WINDOW_SECONDS
    state_path = tmp_path / "prime-state.json"
    state_path.write_text(
        json.dumps({"__row_cooldowns__": {row_id: {"primed_at_ts": 1_000_000 - 60}}}),
        encoding="utf-8",
    )
    calls = []

    monkeypatch.setattr(module, "PRIME_STATE_PATH", state_path)
    monkeypatch.setattr(module.time, "time", lambda: 1_000_000)
    monkeypatch.setattr(module, "prime_five_hour_row", lambda *args, **kwargs: calls.append(args) or {"ok": True})

    result = module.prime_full_five_hour_rows([target_row], model="gpt-test")

    assert calls == []
    assert result["triggered"] == []
    assert result["skipped"] == [{"row_id": row_id, "reason": "recently_primed"}]


def test_prime_five_hour_row_posts_minimal_codex_response(monkeypatch):
    module = load_sync_module()
    client = _PrimeClient()
    monkeypatch.setattr(module.httpx, "Client", lambda timeout=15.0: client)
    target_row = row("auth.full.json", "full", five_hour=100)
    auth_data = {
        "auth_mode": "chatgpt",
        "tokens": {
            "access_token": "access-token",
            "refresh_token": "refresh-token",
            "account_id": "acct_123",
        },
    }

    result = module.prime_five_hour_row(target_row, auth_data, model="gpt-test")

    assert result["ok"] is True
    assert result["response_id"] == "resp_prime_123"
    assert len(client.requests) == 1
    request = client.requests[0]
    assert request["url"] == "https://chatgpt.com/backend-api/codex/responses"
    assert request["headers"]["Authorization"] == "Bearer access-token"
    assert request["headers"]["ChatGPT-Account-ID"] == "acct_123"
    assert request["json"] == {
        "model": "gpt-test",
        "instructions": "Reply with exactly: .",
        "input": [{"role": "user", "content": "."}],
        "store": False,
        "stream": True,
    }
