from __future__ import annotations

import importlib.util
import plistlib
from importlib.machinery import SourceFileLoader
from pathlib import Path


def load_script(name: str):
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / name
    loader = SourceFileLoader(name.replace(".", "_"), str(script_path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_watcher_fingerprint_changes_when_watched_file_changes(tmp_path):
    watcher = load_script("HermesCodexAccountSyncWatcher")
    watched = tmp_path / "last-menu-rows.json"
    watched.write_text("[]", encoding="utf-8")

    first = watcher.fingerprint([watched])
    watched.write_text("[{}]", encoding="utf-8")
    second = watcher.fingerprint([watched])

    assert first != second


def test_installer_renders_repo_owned_watcher_plist(monkeypatch, tmp_path):
    installer = load_script("install_codex_menubar_sync_watcher.py")
    watcher = tmp_path / "HermesCodexAccountSyncWatcher"
    watcher.write_text("#!/usr/bin/env python3\n", encoding="utf-8")

    monkeypatch.setattr(installer, "WATCHER", watcher)
    monkeypatch.setattr(installer, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(installer, "LAUNCH_AGENTS", tmp_path / "LaunchAgents")
    monkeypatch.setattr(installer, "LOG_DIR", tmp_path / "Logs")
    monkeypatch.setattr(installer, "PLIST_PATH", tmp_path / "LaunchAgents" / f"{installer.LABEL}.plist")
    monkeypatch.setattr(installer, "STDOUT_LOG", tmp_path / "Logs" / "stdout.log")
    monkeypatch.setattr(installer, "STDERR_LOG", tmp_path / "Logs" / "stderr.log")

    assert installer.install(interval=7.0, load=False) == 0

    with installer.PLIST_PATH.open("rb") as fh:
        plist = plistlib.load(fh)
    assert plist["Label"] == installer.LABEL
    assert plist["ProgramArguments"] == [str(watcher), "--interval", "7.0"]
    assert plist["RunAtLoad"] is True
    assert plist["KeepAlive"] is True
    assert plist["WorkingDirectory"] == str(tmp_path)
    path_parts = plist["EnvironmentVariables"]["PATH"].split(":")
    assert path_parts[:2] == ["/opt/homebrew/bin", "/usr/local/bin"]
    assert str(Path.home() / ".hermes/bin") in path_parts
