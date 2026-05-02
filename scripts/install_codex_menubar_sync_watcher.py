#!/usr/bin/env python3
"""Install the repo-owned Codex Menubar -> Hermes auth sync watcher as a LaunchAgent."""
from __future__ import annotations

import argparse
import os
import plistlib
import subprocess
import sys
from pathlib import Path

LABEL = "com.hermes.codex-menubar-account-sync-watcher"
HOME = Path.home()
REPO_ROOT = Path(__file__).resolve().parents[1]
WATCHER = REPO_ROOT / "scripts" / "HermesCodexAccountSyncWatcher"
LAUNCH_AGENTS = HOME / "Library" / "LaunchAgents"
LOG_DIR = HOME / "Library" / "Logs" / "Hermes"
PLIST_PATH = LAUNCH_AGENTS / f"{LABEL}.plist"
STDOUT_LOG = LOG_DIR / "codex_menubar_sync_watcher.stdout.log"
STDERR_LOG = LOG_DIR / "codex_menubar_sync_watcher.stderr.log"
DEFAULT_LAUNCHD_PATH = ":".join(
    [
        "/opt/homebrew/bin",
        "/usr/local/bin",
        "/usr/bin",
        "/bin",
        "/usr/sbin",
        "/sbin",
        str(HOME / ".local/bin"),
        str(HOME / ".hermes/bin"),
    ]
)


def render_plist(interval: float) -> dict:
    return {
        "Label": LABEL,
        "ProgramArguments": [str(WATCHER), "--interval", str(interval)],
        "RunAtLoad": True,
        "KeepAlive": True,
        "WorkingDirectory": str(REPO_ROOT),
        "StandardOutPath": str(STDOUT_LOG),
        "StandardErrorPath": str(STDERR_LOG),
        "EnvironmentVariables": {"PATH": DEFAULT_LAUNCHD_PATH},
    }


def run_launchctl(args: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["launchctl", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=check)


def install(interval: float, load: bool = True) -> int:
    if not WATCHER.exists():
        print(f"missing watcher: {WATCHER}", file=sys.stderr)
        return 1
    WATCHER.chmod(WATCHER.stat().st_mode | 0o111)
    LAUNCH_AGENTS.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with PLIST_PATH.open("wb") as fh:
        plistlib.dump(render_plist(interval), fh, sort_keys=False)

    if not load:
        print(str(PLIST_PATH))
        return 0

    domain = f"gui/{os.getuid()}"
    run_launchctl(["bootout", domain, str(PLIST_PATH)], check=False)
    bootstrap = run_launchctl(["bootstrap", domain, str(PLIST_PATH)], check=False)
    if bootstrap.returncode != 0 and "already bootstrapped" not in bootstrap.stdout.lower():
        print(bootstrap.stdout, file=sys.stderr, end="")
        return bootstrap.returncode
    run_launchctl(["enable", f"{domain}/{LABEL}"], check=False)
    run_launchctl(["kickstart", "-k", f"{domain}/{LABEL}"], check=False)
    print(str(PLIST_PATH))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install Codex Menubar -> Hermes auth sync watcher LaunchAgent")
    parser.add_argument("--interval", type=float, default=5.0, help="Watcher polling interval in seconds")
    parser.add_argument("--no-load", action="store_true", help="Only write the plist; do not bootstrap it")
    args = parser.parse_args(argv)
    return install(interval=args.interval, load=not args.no_load)


if __name__ == "__main__":
    raise SystemExit(main())
