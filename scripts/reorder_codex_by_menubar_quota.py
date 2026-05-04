#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
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

import httpx

try:
    import tomllib
except ImportError:  # pragma: no cover - Python <3.11 fallback
    tomllib = None

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
FIVE_HOUR_WINDOW_SECONDS = 5 * 60 * 60
FIVE_HOUR_PRIME_TOLERANCE_SECONDS = 30 * 60
FIVE_HOUR_PRIME_COOLDOWN_SECONDS = FIVE_HOUR_WINDOW_SECONDS
PRIME_STATE_PATH = HOME / ".hermes/codex-five-hour-prime-state.json"
PRIME_STATE_COOLDOWN_KEY = "__row_cooldowns__"
CODEX_CONFIG_PATH = CODEX_HOME / "config.toml"
DEFAULT_CODEX_PRIME_MODEL = "gpt-5.4"
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


def _unix_ts(value: Any) -> int | None:
    if isinstance(value, (int, float)):
        return int(value)
    return None


def _latest_five_hour_trend_point(row: dict[str, Any]) -> dict[str, Any] | None:
    points = row.get("fiveHourTrendPoints")
    if not isinstance(points, list):
        return None
    dict_points = [point for point in points if isinstance(point, dict)]
    if not dict_points:
        return None
    return max(dict_points, key=lambda point: _unix_ts(point.get("recordedAt")) or 0)


def _five_hour_reset_delta_seconds(row: dict[str, Any], now_ts: int) -> int | None:
    reset_at = _unix_ts(row.get("fiveHourResetAt"))
    if reset_at is None:
        return None
    latest = _latest_five_hour_trend_point(row)
    if latest is not None and quota_percent(latest, "remainingPercent") == 100.0:
        trend_reset_at = _unix_ts(latest.get("resetAt"))
        recorded_at = _unix_ts(latest.get("recordedAt"))
        if trend_reset_at is not None and recorded_at is not None:
            return trend_reset_at - recorded_at
    return reset_at - now_ts


def should_prime_five_hour_window(row: dict[str, Any], *, now_ts: int | None = None) -> bool:
    if not isinstance(row.get("id"), str):
        return False
    if str(row.get("usageState") or "").strip().lower() != "ok":
        return False
    if quota_percent(row, "fiveHourRemainingPercent") != 100.0:
        return False
    now_value = int(time.time()) if now_ts is None else int(now_ts)
    reset_at = _unix_ts(row.get("fiveHourResetAt"))
    if reset_at is None or reset_at <= now_value:
        return False
    delta = _five_hour_reset_delta_seconds(row, now_value)
    if delta is None:
        return False
    return abs(delta - FIVE_HOUR_WINDOW_SECONDS) <= FIVE_HOUR_PRIME_TOLERANCE_SECONDS


def five_hour_prime_candidates(rows: list[dict[str, Any]], *, now_ts: int | None = None) -> list[dict[str, Any]]:
    return [row for row in rows if isinstance(row, dict) and should_prime_five_hour_window(row, now_ts=now_ts)]


def _codex_account_id_from_access_token(access_token: str) -> str | None:
    try:
        parts = str(access_token or "").split(".")
        if len(parts) < 2:
            return None
        payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload_b64))
        account_id = claims.get("https://api.openai.com/auth", {}).get("chatgpt_account_id")
        return account_id if isinstance(account_id, str) and account_id.strip() else None
    except Exception:
        return None


def _codex_prime_headers(access_token: str, account_id: str | None) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "codex_cli_rs/0.0.0 (Hermes Agent)",
        "originator": "codex_cli_rs",
    }
    resolved_account_id = (account_id or "").strip() or _codex_account_id_from_access_token(access_token)
    if resolved_account_id:
        headers["ChatGPT-Account-ID"] = resolved_account_id
    return headers


def resolve_prime_model(explicit_model: str | None = None) -> str:
    explicit = str(explicit_model or "").strip()
    if explicit:
        return explicit
    env_model = os.getenv("HERMES_CODEX_PRIME_MODEL", "").strip()
    if env_model:
        return env_model
    if tomllib is not None and CODEX_CONFIG_PATH.exists():
        try:
            data = tomllib.loads(CODEX_CONFIG_PATH.read_text(encoding="utf-8"))
            model = str(data.get("model") or "").strip() if isinstance(data, dict) else ""
            if model:
                return model
        except Exception:
            pass
    return DEFAULT_CODEX_PRIME_MODEL


def _extract_codex_response_id(response_text: str) -> str | None:
    for line in str(response_text or "").splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        data_text = line[len("data:") :].strip()
        if not data_text or data_text == "[DONE]":
            continue
        try:
            event = json.loads(data_text)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        response = event.get("response")
        if isinstance(response, dict) and isinstance(response.get("id"), str):
            return response["id"]
        item = event.get("item")
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            return item["id"]
    return None


def prime_five_hour_row(row: dict[str, Any], auth_data: dict[str, Any], *, model: str | None = None) -> dict[str, Any]:
    tokens = auth_data.get("tokens") or {}
    access_token = str(tokens.get("access_token") or "").strip()
    if not access_token:
        raise ValueError(f"missing access token for {row.get('id')}")
    account_id = tokens.get("account_id")
    payload = {
        "model": resolve_prime_model(model),
        "instructions": "Reply with exactly: .",
        "input": [{"role": "user", "content": "."}],
        "store": False,
        "stream": True,
    }
    with httpx.Client(timeout=15.0) as client:
        response = client.post(
            f"{CODEX_BASE_URL}/responses",
            headers=_codex_prime_headers(access_token, account_id if isinstance(account_id, str) else None),
            json=payload,
        )
        response.raise_for_status()
    return {
        "ok": True,
        "row_id": row.get("id"),
        "label": label_from_row(row),
        "model": payload["model"],
        "response_id": _extract_codex_response_id(getattr(response, "text", "")),
    }


def prime_state_key(row: dict[str, Any]) -> str:
    return f"{row.get('id')}:{row.get('fiveHourResetAt')}"


def load_prime_state(path: Path | None = None) -> dict[str, Any]:
    state_path = path or PRIME_STATE_PATH
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except FileNotFoundError:
        return {}
    except Exception:
        return {}


def save_prime_state(state: dict[str, Any], path: Path | None = None) -> None:
    write_json_atomic(path or PRIME_STATE_PATH, state)


def row_recently_primed(state: dict[str, Any], row_id: str, *, now_ts: int | None = None) -> bool:
    cooldowns = state.get(PRIME_STATE_COOLDOWN_KEY)
    if not isinstance(cooldowns, dict):
        return False
    entry = cooldowns.get(row_id)
    if not isinstance(entry, dict):
        return False
    primed_at = entry.get("primed_at_ts")
    if not isinstance(primed_at, (int, float)):
        return False
    now_value = int(time.time()) if now_ts is None else int(now_ts)
    return 0 <= now_value - int(primed_at) < FIVE_HOUR_PRIME_COOLDOWN_SECONDS


def remember_row_prime(state: dict[str, Any], row: dict[str, Any], result: dict[str, Any], *, now_ts: int | None = None) -> None:
    row_id = str(row.get("id") or "")
    if not row_id:
        return
    now_value = int(time.time()) if now_ts is None else int(now_ts)
    cooldowns = state.setdefault(PRIME_STATE_COOLDOWN_KEY, {})
    if not isinstance(cooldowns, dict):
        cooldowns = {}
        state[PRIME_STATE_COOLDOWN_KEY] = cooldowns
    cooldowns[row_id] = {
        "primed_at_ts": now_value,
        "primed_at": dt.datetime.fromtimestamp(now_value, tz=dt.timezone.utc).isoformat(),
        "fiveHourResetAt": row.get("fiveHourResetAt"),
        "response_id": result.get("response_id"),
        "model": result.get("model"),
    }


def _auth_data_for_row(row: dict[str, Any]) -> dict[str, Any]:
    row_id = str(row.get("id") or "")
    path = CODEX_HOME / ("auth.json" if row.get("isCurrent") is True else row_id)
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"invalid Codex auth payload in {path}")
    return data


def prime_full_five_hour_rows(rows: list[dict[str, Any]], *, model: str | None = None) -> dict[str, Any]:
    candidates = five_hour_prime_candidates(rows)
    state = load_prime_state()
    triggered: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    state_changed = False
    now_ts = int(time.time())
    for row in candidates:
        row_id = str(row.get("id") or "")
        key = prime_state_key(row)
        if key in state:
            skipped.append({"row_id": row.get("id"), "reason": "already_primed_for_reset"})
            continue
        if row_id and row_recently_primed(state, row_id, now_ts=now_ts):
            skipped.append({"row_id": row.get("id"), "reason": "recently_primed"})
            continue
        try:
            result = prime_five_hour_row(row, _auth_data_for_row(row), model=model)
        except Exception as exc:  # noqa: BLE001 - report per-account and keep syncing others
            failed.append({"row_id": row.get("id"), "reason": str(exc)})
            continue
        triggered.append(result)
        state[key] = {
            "row_id": row.get("id"),
            "fiveHourResetAt": row.get("fiveHourResetAt"),
            "primed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "response_id": result.get("response_id"),
            "model": result.get("model"),
        }
        remember_row_prime(state, row, result, now_ts=now_ts)
        state_changed = True
    if state_changed:
        save_prime_state(state)
    return {
        "candidates": [{"row_id": row.get("id"), "label": label_from_row(row)} for row in candidates],
        "triggered": triggered,
        "skipped": skipped,
        "failed": failed,
    }


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
    parser.add_argument(
        "--prime-full-five-hour",
        action="store_true",
        help="When applying, send one minimal Codex response for 100% five-hour rows whose reset is still a full five-hour window away",
    )
    parser.add_argument("--prime-model", default=None, help="Model to use for the minimal Codex priming response; defaults to HERMES_CODEX_PRIME_MODEL, ~/.codex/config.toml, then gpt-5.4")
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

    five_hour_prime = None
    if args.apply and args.prime_full_five_hour:
        five_hour_prime = prime_full_five_hour_rows(ranked_rows, model=args.prime_model)

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
        "five_hour_prime": five_hour_prime,
        "strategy_note": "preserves CodexMaintainerMenubar last-menu-rows.json order exactly; that file is already written after UsageRefreshService.ranked(...), so the first row is the Menubar top-ranked account and becomes Hermes openai-codex priority 0 / provider singleton when --apply is used; labels use account-plan-fiveHourPercent-weeklyPercent format; with --prime-full-five-hour, 100% five-hour rows whose reset is still a full five-hour window away are triggered once with a minimal non-stored Codex response so the five-hour refresh anchor can start",
    }
    if args.quiet:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
