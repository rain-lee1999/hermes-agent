#!/usr/bin/env bash
# Install macOS launchd/Login Items declared in scripts/macos-login-items.md.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SHEET="${MACOS_LOGIN_ITEMS_SHEET:-$SCRIPT_DIR/macos-login-items.md}"
SETUP_PYTHON="${SETUP_PYTHON:-$REPO_ROOT/venv/bin/python}"

if [ "${MACOS_LOGIN_ITEMS_FORCE_DARWIN:-}" != "1" ] && [ "$(uname -s)" != "Darwin" ]; then
    exit 0
fi

if [ ! -f "$SHEET" ]; then
    echo "missing macOS login item sheet: $SHEET" >&2
    exit 1
fi

PARSER_PYTHON="$SETUP_PYTHON"
if [ ! -x "$PARSER_PYTHON" ]; then
    if command -v python3 >/dev/null 2>&1; then
        PARSER_PYTHON="$(command -v python3)"
    elif command -v python >/dev/null 2>&1; then
        PARSER_PYTHON="$(command -v python)"
    else
        echo "missing Python for macOS login item sheet parser" >&2
        exit 1
    fi
fi

export SETUP_PYTHON
exec "$PARSER_PYTHON" - "$REPO_ROOT" "$SHEET" <<'PY'
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

repo_root = Path(sys.argv[1])
sheet = Path(sys.argv[2])
setup_python = Path(os.environ.get("SETUP_PYTHON") or repo_root / "venv/bin/python")
required_fields = ("kind", "label", "installer", "verify")
valid_kinds = {"launchagent", "loginitem"}
field_aliases = {
    "launchd_label": "label",
    "login_item_label": "label",
    "identifier": "label",
}


def strip_markdown_value(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`") and len(value) >= 2:
        value = value[1:-1]
    return value.strip()


def parse_field(line: str) -> tuple[str, str] | None:
    if not line.startswith("-"):
        return None
    content = line[1:].strip().replace("**", "")
    if ":" not in content:
        return None
    key, value = content.split(":", 1)
    key = key.strip().lower().replace(" ", "_")
    key = field_aliases.get(key, key)
    value = strip_markdown_value(value)
    return key, value


def finalize_item(item: dict[str, object] | None, items: list[dict[str, str]]) -> None:
    if item is None:
        return
    fields = item["fields"]
    assert isinstance(fields, dict)
    missing = [field for field in required_fields if not fields.get(field)]
    if missing:
        line = item.get("line", "?")
        title = item.get("title", "unnamed item")
        raise SystemExit(f"{sheet}:{line}: item '{title}' is missing field(s): {', '.join(missing)}")

    enabled = str(fields.get("enabled", "yes")).strip().lower()
    if enabled in {"no", "false", "0", "disabled", "skip"}:
        return
    if enabled not in {"yes", "true", "1", "enabled"}:
        line = item.get("line", "?")
        raise SystemExit(f"{sheet}:{line}: Enabled must be yes or no, got '{fields.get('enabled')}'")

    kind = str(fields["kind"]).strip().lower()
    if kind not in valid_kinds:
        line = item.get("line", "?")
        raise SystemExit(f"{sheet}:{line}: unsupported Kind '{fields['kind']}'")

    items.append(
        {
            "kind": kind,
            "label": str(fields["label"]).strip(),
            "description": str(fields.get("description") or item.get("title") or fields["label"]).strip(),
            "installer": str(fields["installer"]).strip(),
            "verify": str(fields["verify"]).strip(),
        }
    )


def parse_items() -> list[dict[str, str]]:
    current: dict[str, object] | None = None
    items: list[dict[str, str]] = []
    in_code_block = False
    for line_no, raw_line in enumerate(sheet.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if line.startswith("## Item:"):
            finalize_item(current, items)
            current = {"title": line.split(":", 1)[1].strip(), "line": line_no, "fields": {}}
            continue
        if current is None:
            continue
        parsed = parse_field(line)
        if parsed:
            key, value = parsed
            current_fields = current["fields"]
            assert isinstance(current_fields, dict)
            current_fields[key] = value
    finalize_item(current, items)
    return items


def resolve_path(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return repo_root / candidate


def run_installer(installer: Path) -> None:
    if installer.suffix == ".py":
        if not setup_python.exists():
            raise SystemExit(f"missing setup Python for Python installer: {setup_python}")
        subprocess.run([str(setup_python), str(installer)], check=True)
    elif installer.suffix == ".sh":
        subprocess.run(["bash", str(installer)], check=True)
    else:
        subprocess.run([str(installer)], check=True)


def main() -> int:
    items = parse_items()
    if not items:
        print(f"No enabled macOS launchd/Login Items declared in {sheet}")
        return 0

    uid = str(os.getuid())
    for item in items:
        installer = resolve_path(item["installer"])
        if not installer.is_file():
            raise SystemExit(f"{sheet}: missing installer for {item['label']}: {installer}")

        print(f"→ Installing {item['kind']}: {item['description']}")
        run_installer(installer)
        print(f"✓ Installed and started: {item['label']}")
        print(f"  Verify: {item['verify'].replace('{uid}', uid)}")
    return 0


raise SystemExit(main())
PY
