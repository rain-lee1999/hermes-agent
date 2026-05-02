#!/usr/bin/env python3
from __future__ import annotations

import argparse
from contextlib import contextmanager
import datetime as dt
import json
import os
import shutil
import sys
import time
import uuid
from pathlib import Path
from typing import Any

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX fallback
    fcntl = None

HOME = Path.home()
APP_ROWS_PATH = HOME / "Library/Application Support/CodexMaintainerMenubar/last-menu-rows.json"
HERMES_AUTH_PATH = HOME / ".hermes/auth.json"
CODEX_HOME = HOME / ".codex"
BACKUP_DIR = HOME / ".hermes/backups"
CODEX_BASE_URL = "https://chatgpt.com/backend-api/codex"
FIVE_HOUR_MIN_REMAINING_PERCENT = 5.0
AUTH_LOCK_TIMEOUT_SECONDS = 30.0


def normalize_weight(plan_type: str, quota_weight: Any) -> float:
    if isinstance(quota_weight, (int, float)):
        if quota_weight == quota_weight and quota_weight not in (float("inf"), float("-inf")):
            return round(min(max(float(quota_weight), 0.0), 100.0), 1)
    return 0.1 if str(plan_type or "").strip().lower() == "free" else 1.0


def quota_percent(row: dict[str, Any], key: str) -> float | None:
    value = row.get(key)
    if isinstance(value, (int, float)):
        return max(0.0, min(100.0, float(value)))
    return None


def effective_remaining_percent(row: dict[str, Any]) -> float:
    weekly = quota_percent(row, "weeklyRemainingPercent")
    five_hour = quota_percent(row, "fiveHourRemainingPercent")
    values = [v for v in (weekly, five_hour) if v is not None]
    if not values:
        return -1.0
    return min(values)


def label_percent(row: dict[str, Any]) -> str:
    percent = effective_remaining_percent(row)
    if percent < 0:
        return "--%"
    return f"{int(round(percent))}%"


def quota_label_percent(row: dict[str, Any], key: str) -> str:
    percent = quota_percent(row, key)
    if percent is None:
        return "--%"
    return f"{int(round(percent))}%"


def label_from_row(row: dict[str, Any]) -> str:
    base = label_from_row_id(str(row.get("id") or ""))
    plan = str(row.get("planType") or "unknown").strip().lower() or "unknown"
    five_hour = quota_label_percent(row, "fiveHourRemainingPercent")
    weekly = quota_label_percent(row, "weeklyRemainingPercent")
    return f"{base}-{plan}-{five_hour}-{weekly}"


def state_rank(row: dict[str, Any]) -> int:
    state = str(row.get("usageState") or "").strip().lower()
    if state == "ok":
        return 0
    if state == "loading":
        return 1
    if state == "unsupported":
        return 2
    return 3


def successful_plan_rank(row: dict[str, Any]) -> int:
    plan = str(row.get("planType") or "").strip().lower()
    return 1 if plan == "free" else 0


def five_hour_exhaustion_rank(row: dict[str, Any]) -> int:
    five_hour = quota_percent(row, "fiveHourRemainingPercent")
    return 1 if five_hour is not None and five_hour < FIVE_HOUR_MIN_REMAINING_PERCENT else 0


def remaining_budget_per_day_parts(row: dict[str, Any]) -> tuple[int, int] | None:
    remaining = row.get("weeklyRemainingPercent")
    reset_at = row.get("weeklyResetAt")
    if not isinstance(remaining, (int, float)) or not isinstance(reset_at, int):
        return None
    now = dt.datetime.now()
    reset_date = dt.datetime.fromtimestamp(reset_at)
    current_day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    reset_day_start = reset_date.replace(hour=0, minute=0, second=0, microsecond=0)
    remaining_days = max((reset_day_start.date() - current_day_start.date()).days, 1)
    return int(round(float(remaining))), remaining_days


def compare_remaining_budget_per_day(lhs: dict[str, Any], rhs: dict[str, Any]) -> int:
    lhs_parts = remaining_budget_per_day_parts(lhs)
    rhs_parts = remaining_budget_per_day_parts(rhs)
    if lhs_parts and rhs_parts:
        lhs_remaining, lhs_days = lhs_parts
        rhs_remaining, rhs_days = rhs_parts
        lhs_score = lhs_remaining * rhs_days
        rhs_score = rhs_remaining * lhs_days
        if lhs_score != rhs_score:
            return -1 if lhs_score > rhs_score else 1
    elif lhs_parts and not rhs_parts:
        return -1
    elif rhs_parts and not lhs_parts:
        return 1
    return 0


def row_sort_cmp(lhs: dict[str, Any], rhs: dict[str, Any]) -> int:
    lhs_five_hour_exhaustion = five_hour_exhaustion_rank(lhs)
    rhs_five_hour_exhaustion = five_hour_exhaustion_rank(rhs)
    if lhs_five_hour_exhaustion != rhs_five_hour_exhaustion:
        return -1 if lhs_five_hour_exhaustion < rhs_five_hour_exhaustion else 1

    lhs_state = state_rank(lhs)
    rhs_state = state_rank(rhs)
    if lhs_state != rhs_state:
        return -1 if lhs_state < rhs_state else 1

    if lhs_state == 0 and rhs_state == 0:
        lhs_plan = successful_plan_rank(lhs)
        rhs_plan = successful_plan_rank(rhs)
        if lhs_plan != rhs_plan:
            return -1 if lhs_plan < rhs_plan else 1
        budget_cmp = compare_remaining_budget_per_day(lhs, rhs)
        if budget_cmp:
            return budget_cmp

    lhs_reset = lhs.get("weeklyResetAt")
    rhs_reset = rhs.get("weeklyResetAt")
    if isinstance(lhs_reset, int) and isinstance(rhs_reset, int) and lhs_reset != rhs_reset:
        return -1 if lhs_reset < rhs_reset else 1
    if isinstance(lhs_reset, int) and not isinstance(rhs_reset, int):
        return -1
    if not isinstance(lhs_reset, int) and isinstance(rhs_reset, int):
        return 1

    lhs_name = str(lhs.get("displayName") or lhs.get("id") or "").lower()
    rhs_name = str(rhs.get("displayName") or rhs.get("id") or "").lower()
    if lhs_name < rhs_name:
        return -1
    if lhs_name > rhs_name:
        return 1
    return 0


def ranking_debug_value(row: dict[str, Any]) -> str:
    parts = remaining_budget_per_day_parts(row)
    if parts:
        remaining, days = parts
        return f"{remaining}/{days}d"
    return "n/a"


def sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        five_hour_exhaustion_rank(row),
        state_rank(row),
        successful_plan_rank(row),
        -(remaining_budget_per_day_parts(row)[0] / remaining_budget_per_day_parts(row)[1]) if remaining_budget_per_day_parts(row) else float("inf"),
        row.get("weeklyResetAt") if isinstance(row.get("weeklyResetAt"), int) else 2**31 - 1,
        str(row.get("displayName") or row.get("id") or "").lower(),
    )


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        os.replace(tmp_path, path)
    finally:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass


@contextmanager
def auth_store_lock(auth_path: Path):
    lock_path = auth_path.with_suffix(".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as lock_file:
        if fcntl is not None:
            deadline = time.monotonic() + AUTH_LOCK_TIMEOUT_SECONDS
            while True:
                try:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError(f"timed out waiting for auth lock: {lock_path}")
                    time.sleep(0.05)
        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def backup_file(path: Path) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = BACKUP_DIR / f"{path.name}.pre-menubar-sync.{stamp}.bak"
    shutil.copy2(path, backup)
    return backup


def build_ranking(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    # CodexMaintainerMenubar already persists last-menu-rows.json in
    # UsageRefreshService.ranked(...) order. Preserve that order exactly so
    # Hermes selects the same top-ranked account instead of reimplementing a
    # possibly stale copy of the Menubar ranking logic here.
    ranked = [row for row in rows if isinstance(row, dict) and isinstance(row.get("id"), str)]
    return ranked, {str(row["id"]): row for row in ranked}


def label_from_row_id(row_id: str) -> str:
    if row_id.startswith("auth.") and row_id.endswith(".json"):
        core = row_id[len("auth.") : -len(".json")]
        return core or row_id
    return row_id


def _entry_payload_from_auth_data(
    data: dict[str, Any],
    *,
    row_id: str,
    row: dict[str, Any] | None,
    source: str,
) -> dict[str, Any]:
    tokens = data.get("tokens") or {}
    access = tokens.get("access_token")
    refresh = tokens.get("refresh_token")
    if not access or not refresh:
        raise ValueError(f"missing access/refresh token in auth payload for {row_id}")
    payload = {
        "label": label_from_row(row) if row else label_from_row_id(row_id),
        "auth_type": "oauth",
        "source": source,
        "access_token": access,
        "refresh_token": refresh,
        "last_status": None,
        "last_status_at": None,
        "last_error_code": None,
        "last_error_reason": None,
        "last_error_message": None,
        "last_error_reset_at": None,
        "base_url": CODEX_BASE_URL,
        "last_refresh": data.get("last_refresh"),
        "request_count": 0,
        "account_id": tokens.get("account_id"),
        "auth_mode": data.get("auth_mode"),
        "imported_from": row_id,
    }
    id_token = tokens.get("id_token")
    client_id = tokens.get("client_id")
    if id_token:
        payload["id_token"] = id_token
    if client_id:
        payload["client_id"] = client_id
    return payload


def create_entry_from_codex_file(row_id: str, row: dict[str, Any] | None = None) -> dict[str, Any]:
    path = CODEX_HOME / row_id
    if not path.exists():
        raise FileNotFoundError(str(path))
    data = load_json(path)
    return {
        "id": uuid.uuid4().hex[:6],
        "priority": 0,
        **_entry_payload_from_auth_data(
            data,
            row_id=row_id,
            row=row,
            source=f"manual:codex-file:{row_id}",
        ),
    }


def current_codex_auth_data() -> dict[str, Any]:
    path = CODEX_HOME / "auth.json"
    if not path.exists():
        raise FileNotFoundError(str(path))
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"invalid current Codex auth payload in {path}")
    return data


def row_id_from_entry(entry: dict[str, Any]) -> str | None:
    imported_from = entry.get("imported_from")
    if imported_from:
        return str(imported_from)
    source = str(entry.get("source") or "")
    prefix = "manual:codex-file:"
    if source.startswith(prefix):
        row_id = source[len(prefix):].strip()
        return row_id or None
    return None


def resolve_entry_row(
    entry: dict[str, Any],
    row_lookup: dict[str, dict[str, Any]],
    current_row: dict[str, Any] | None,
) -> tuple[str | None, dict[str, Any] | None]:
    imported_from = row_id_from_entry(entry)
    if imported_from:
        row = row_lookup.get(str(imported_from))
        if row is not None:
            return str(imported_from), row
    if entry.get("source") == "device_code" and current_row is not None:
        current_id = current_row.get("id")
        if isinstance(current_id, str):
            return current_id, current_row
    return None, None


def sync_entries(
    entries: list[dict[str, Any]],
    row_lookup: dict[str, dict[str, Any]],
    current_row: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    current_row_id = current_row.get("id") if isinstance(current_row, dict) else None
    desired_noncurrent_ids = [row_id for row_id in row_lookup.keys() if row_id != current_row_id]
    entry_by_imported_from: dict[str, dict[str, Any]] = {}
    kept_entries: list[dict[str, Any]] = []
    removed_entries: list[dict[str, Any]] = []
    seen_noncurrent_imported_from: set[str] = set()
    kept_device_code = False

    for entry in entries:
        if entry.get("source") == "device_code":
            if kept_device_code or not current_row_id:
                removed_entries.append(entry)
                continue
            updated = dict(entry)
            current_data = current_codex_auth_data()
            updated.update(
                _entry_payload_from_auth_data(
                    current_data,
                    row_id=str(current_row_id),
                    row=current_row,
                    source="device_code",
                )
            )
            kept_entries.append(updated)
            entry_by_imported_from[str(current_row_id)] = updated
            kept_device_code = True
            continue
        imported_from = row_id_from_entry(entry)
        if not imported_from:
            kept_entries.append(entry)
            continue
        imported_from = str(imported_from)
        if imported_from not in row_lookup or imported_from == current_row_id:
            removed_entries.append(entry)
            continue
        if imported_from in seen_noncurrent_imported_from:
            removed_entries.append(entry)
            continue
        seen_noncurrent_imported_from.add(imported_from)
        updated = dict(entry)
        updated.update(
            _entry_payload_from_auth_data(
                load_json(CODEX_HOME / imported_from),
                row_id=imported_from,
                row=row_lookup[imported_from],
                source=updated.get("source") or f"manual:codex-file:{imported_from}",
            )
        )
        entry_by_imported_from[imported_from] = updated
        kept_entries.append(updated)

    added_entries: list[dict[str, Any]] = []
    skipped_adds: list[dict[str, Any]] = []
    for row_id in desired_noncurrent_ids:
        if row_id in entry_by_imported_from:
            continue
        try:
            entry = create_entry_from_codex_file(row_id, row_lookup.get(row_id))
        except Exception as exc:  # noqa: BLE001
            skipped_adds.append({"row_id": row_id, "reason": str(exc)})
            continue
        kept_entries.append(entry)
        entry_by_imported_from[row_id] = entry
        added_entries.append(entry)

    return kept_entries, added_entries, removed_entries, skipped_adds


def reorder_entries(
    entries: list[dict[str, Any]],
    row_lookup: dict[str, dict[str, Any]],
    current_row: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    row_rank = {row_id: index for index, row_id in enumerate(row_lookup.keys())}
    unmatched_rank = len(row_rank)
    matched: list[tuple[int, int, dict[str, Any], dict[str, Any], str]] = []
    unmatched: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        matched_id, row = resolve_entry_row(entry, row_lookup, current_row)
        if row is None or matched_id is None:
            unmatched.append(entry)
            continue
        matched.append((row_rank.get(matched_id, unmatched_rank), index, entry, row, matched_id))
    matched.sort(key=lambda item: (item[0], item[1]))
    ordered = [(entry, matched_id, row) for _, _, entry, row, matched_id in matched] + [(entry, None, None) for entry in unmatched]
    result = []
    movement = []
    for priority, (entry, matched_id, row) in enumerate(ordered):
        old_priority = entry.get("priority")
        updated = dict(entry)
        updated["priority"] = priority
        result.append(updated)
        movement.append(
            {
                "label": updated.get("label"),
                "matched_row_id": matched_id,
                "imported_from": updated.get("imported_from"),
                "old_priority": old_priority,
                "new_priority": priority,
                "score": ranking_debug_value(row) if row is not None else None,
                "five_hour_below_minimum": bool(five_hour_exhaustion_rank(row)) if row is not None else False,
            }
        )
    ranked_matches = [
        {
            "id": row.get("id"),
            "displayName": row.get("displayName"),
            "planType": row.get("planType"),
            "effectiveRemainingPercent": effective_remaining_percent(row),
            "weeklyRemainingPercent": row.get("weeklyRemainingPercent"),
            "fiveHourRemainingPercent": row.get("fiveHourRemainingPercent"),
            "quotaWeight": normalize_weight(str(row.get("planType") or ""), row.get("quotaWeight")),
            "fiveHourBelowMinimum": bool(five_hour_exhaustion_rank(row)),
            "score": ranking_debug_value(row),
        }
        for row in row_lookup.values()
    ]
    return result, movement, ranked_matches


def signature(entries: list[dict[str, Any]]) -> list[tuple[Any, ...]]:
    return [
        (
            entry.get("label"),
            entry.get("source"),
            entry.get("imported_from"),
            entry.get("priority"),
            entry.get("account_id"),
        )
        for entry in entries
    ]


def summarize_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": entry.get("label"),
        "source": entry.get("source"),
        "imported_from": entry.get("imported_from"),
        "account_id": entry.get("account_id"),
    }


def sync_provider_singleton_from_primary_entry(auth_store: dict[str, Any], reordered: list[dict[str, Any]]) -> bool:
    if not reordered:
        return False
    primary = reordered[0]
    access_token = str(primary.get("access_token") or "").strip()
    refresh_token = str(primary.get("refresh_token") or "").strip()
    if not access_token or not refresh_token:
        return False

    providers = auth_store.setdefault("providers", {})
    if not isinstance(providers, dict):
        providers = {}
        auth_store["providers"] = providers
    state = providers.get("openai-codex")
    if not isinstance(state, dict):
        state = {}

    tokens = state.get("tokens")
    if not isinstance(tokens, dict):
        tokens = {}
    tokens = dict(tokens)
    changed = False
    desired_fields = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
    for optional_key in ("account_id", "client_id", "id_token"):
        optional_value = primary.get(optional_key)
        if isinstance(optional_value, str) and optional_value.strip():
            desired_fields[optional_key] = optional_value.strip()
    for key, value in desired_fields.items():
        if tokens.get(key) != value:
            tokens[key] = value
            changed = True

    last_refresh = primary.get("last_refresh")
    if isinstance(last_refresh, str) and last_refresh.strip() and state.get("last_refresh") != last_refresh:
        state["last_refresh"] = last_refresh
        changed = True
    if state.get("auth_mode") != "chatgpt":
        state["auth_mode"] = "chatgpt"
        changed = True

    if not changed:
        return False

    state["tokens"] = tokens
    providers["openai-codex"] = state
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Hermes openai-codex credentials from CodexMaintainerMenubar quota snapshots.")
    parser.add_argument("--apply", action="store_true", help="Write the synced priorities and add/delete changes back to ~/.hermes/auth.json")
    parser.add_argument("--quiet", action="store_true", help="Only print JSON")
    args = parser.parse_args()

    if not APP_ROWS_PATH.exists():
        raise SystemExit(f"Missing menubar rows file: {APP_ROWS_PATH}")
    if not HERMES_AUTH_PATH.exists():
        raise SystemExit(f"Missing Hermes auth file: {HERMES_AUTH_PATH}")

    rows = load_json(APP_ROWS_PATH)
    if not isinstance(rows, list):
        raise SystemExit("last-menu-rows.json is not a JSON array")
    ranked_rows, row_lookup = build_ranking(rows)
    current_row = next((row for row in rows if isinstance(row, dict) and row.get("isCurrent") is True), None)

    with auth_store_lock(HERMES_AUTH_PATH):
        auth_store = load_json(HERMES_AUTH_PATH)
        credential_pool = auth_store.get("credential_pool") or {}
        entries = credential_pool.get("openai-codex") or []
        if not isinstance(entries, list):
            raise SystemExit("Hermes auth openai-codex credential pool is not a list")

        synced_entries, added_entries, removed_entries, skipped_adds = sync_entries(entries, row_lookup, current_row)
        reordered, movement, ranked_matches = reorder_entries(synced_entries, row_lookup, current_row)

        changed = signature(entries) != signature(reordered)
        provider_synced = sync_provider_singleton_from_primary_entry(auth_store, reordered)
        write_needed = changed or provider_synced
        backup = None
        if args.apply and write_needed:
            backup = str(backup_file(HERMES_AUTH_PATH))
            auth_store.setdefault("credential_pool", {})["openai-codex"] = reordered
            auth_store["updated_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
            write_json_atomic(HERMES_AUTH_PATH, auth_store)

    payload = {
        "app_rows_path": str(APP_ROWS_PATH),
        "hermes_auth_path": str(HERMES_AUTH_PATH),
        "codex_home": str(CODEX_HOME),
        "current_row_id": current_row.get("id") if isinstance(current_row, dict) else None,
        "applied": bool(args.apply and write_needed),
        "changed": changed,
        "provider_synced": provider_synced,
        "backup": backup,
        "added_entries": [summarize_entry(entry) for entry in added_entries],
        "removed_entries": [summarize_entry(entry) for entry in removed_entries],
        "skipped_adds": skipped_adds,
        "matched_entries": [m for m in movement if m.get("matched_row_id")],
        "unmatched_entries": [m for m in movement if not m.get("matched_row_id")],
        "ranked_rows": ranked_matches,
        "strategy_note": "preserves CodexMaintainerMenubar last-menu-rows.json order exactly; that file is already written after UsageRefreshService.ranked(...), so the first row is the Menubar top-ranked account and becomes Hermes openai-codex priority 0 / provider singleton when --apply is used; labels use account-plan-fiveHourPercent-weeklyPercent format",
    }
    if args.quiet:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
