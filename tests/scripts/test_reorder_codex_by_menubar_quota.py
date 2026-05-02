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
