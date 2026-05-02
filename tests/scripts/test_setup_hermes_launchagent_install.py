from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SETUP_SCRIPT = REPO_ROOT / "setup-hermes.sh"
INSTALLER_SCRIPT = REPO_ROOT / "scripts" / "install_macos_login_items.sh"
SHEET = REPO_ROOT / "scripts" / "macos-login-items.md"
LABEL = "com.hermes.codex-menubar-account-sync-watcher"


def test_setup_hermes_shell_syntax_is_valid():
    subprocess.run(["bash", "-n", str(SETUP_SCRIPT)], check=True)
    subprocess.run(["bash", "-n", str(INSTALLER_SCRIPT)], check=True)


def test_setup_hermes_delegates_macos_login_items_to_markdown_installer():
    script = SETUP_SCRIPT.read_text(encoding="utf-8")
    assert "scripts/install_macos_login_items.sh" in script
    assert 'SETUP_PYTHON="$SETUP_PYTHON" "$SCRIPT_DIR/scripts/install_macos_login_items.sh"' in script
    assert "scripts/install_codex_menubar_sync_watcher.py" not in script


def test_macos_login_items_markdown_is_human_readable_and_declares_codex_launchagent():
    markdown = SHEET.read_text(encoding="utf-8")

    assert "# macOS launchd / Login Items installed by `./setup-hermes.sh`" in markdown
    assert "How setup uses this file:" in markdown
    assert "Naming rules:" in markdown
    assert "`## Item: ...` is a human-readable title" in markdown
    assert "`Launchd Label` is the actual stable identifier" in markdown
    assert "Field meanings for each item:" in markdown
    assert "To add another background item" in markdown
    assert "## Item: Codex Menubar -> Hermes auth sync watcher" in markdown
    assert "What setup does for this item:" in markdown

    item_match = re.search(
        r"## Item: Codex Menubar -> Hermes auth sync watcher(?P<body>.*?)(?:\n## Item:|\Z)",
        markdown,
        re.DOTALL,
    )
    assert item_match is not None
    body = item_match.group("body")
    assert "- **Enabled:** `yes`" in body
    assert "- **Kind:** `launchagent`" in body
    assert f"- **Launchd Label:** `{LABEL}`" in body
    assert "- **Installer:** `scripts/install_codex_menubar_sync_watcher.py`" in body
    assert f"- **Verify:** `launchctl print gui/{{uid}}/{LABEL}`" in body


def test_macos_login_items_installer_runs_markdown_items(tmp_path):
    marker = tmp_path / "installed.txt"
    fake_installer = tmp_path / "fake-installer.sh"
    fake_installer.write_text(f"#!/usr/bin/env bash\necho ran > {marker}\n", encoding="utf-8")
    fake_installer.chmod(0o755)
    sheet = tmp_path / "macos-login-items.md"
    sheet.write_text(
        "# Test macOS login items\n\n"
        "## Item: Example Test Item\n\n"
        "- **Enabled:** `yes`\n"
        "- **Kind:** `launchagent`\n"
        "- **Launchd Label:** `com.example.test`\n"
        f"- **Installer:** `{fake_installer}`\n"
        "- **Verify:** `launchctl print gui/{uid}/com.example.test`\n",
        encoding="utf-8",
    )

    env = {**os.environ, "MACOS_LOGIN_ITEMS_FORCE_DARWIN": "1", "MACOS_LOGIN_ITEMS_SHEET": str(sheet)}
    result = subprocess.run(
        ["bash", str(INSTALLER_SCRIPT)],
        check=True,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert marker.read_text(encoding="utf-8") == "ran\n"
    assert "Installed and started: com.example.test" in result.stdout
    assert re.search(r"Verify: launchctl print gui/\d+/com\.example\.test", result.stdout)


def test_macos_login_items_installer_can_skip_disabled_markdown_items(tmp_path):
    marker = tmp_path / "should-not-exist.txt"
    fake_installer = tmp_path / "disabled-installer.sh"
    fake_installer.write_text(f"#!/usr/bin/env bash\necho ran > {marker}\n", encoding="utf-8")
    fake_installer.chmod(0o755)
    sheet = tmp_path / "macos-login-items.md"
    sheet.write_text(
        "# Test macOS login items\n\n"
        "## Item: Disabled Test Item\n\n"
        "- **Enabled:** `no`\n"
        "- **Kind:** `launchagent`\n"
        "- **Launchd Label:** `com.example.disabled`\n"
        f"- **Installer:** `{fake_installer}`\n"
        "- **Verify:** `launchctl print gui/{uid}/com.example.disabled`\n",
        encoding="utf-8",
    )

    env = {**os.environ, "MACOS_LOGIN_ITEMS_FORCE_DARWIN": "1", "MACOS_LOGIN_ITEMS_SHEET": str(sheet)}
    result = subprocess.run(
        ["bash", str(INSTALLER_SCRIPT)],
        check=True,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert not marker.exists()
    assert "No enabled macOS launchd/Login Items declared" in result.stdout
