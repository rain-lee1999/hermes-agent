# macOS launchd / Login Items installed by `./setup-hermes.sh`

This file is the source of truth for macOS background items that should be installed when someone runs `./setup-hermes.sh` from this repo.

How setup uses this file:

1. `./setup-hermes.sh` calls `scripts/install_macos_login_items.sh`.
2. The helper no-ops on non-macOS systems.
3. On macOS, each `## Item:` section below is installed in order.
4. A failed installer stops setup immediately, so setup cannot report success while a Login Item or LaunchAgent is missing.
5. `{uid}` inside a Verify command is replaced with the current GUI user id.

Naming rules:

- `## Item: ...` is a human-readable title for people reading this file. It is not the launchd label.
- `Launchd Label` is the actual stable identifier used by launchd and verification commands.
- Template values like `com.hermes.REPLACE_ME` are placeholders. Replace them with a real reverse-DNS label before enabling a new item.

Field meanings for each item:

- **Enabled:** `yes` installs the item. `no` keeps the item documented but skipped.
- **Kind:** `launchagent` for a user LaunchAgent, or `loginitem` for a Login Item style installer.
- **Launchd Label:** stable launchd/Login Item identifier. It should be unique.
- **Installer:** repo-relative script path. `.py` scripts run with setup's venv Python; `.sh` scripts run with bash.
- **Verify:** command humans can run after setup to confirm the item is installed and loaded.

To add another background item, copy this shape and replace every `REPLACE_ME` value:

```md
## Item: Human-readable item name

- **Enabled:** `yes`
- **Kind:** `launchagent`
- **Launchd Label:** `com.hermes.REPLACE_ME`
- **Installer:** `scripts/install_REPLACE_ME_launchagent.py`
- **Verify:** `launchctl print gui/{uid}/com.hermes.REPLACE_ME`
```

## Item: Codex Menubar -> Hermes auth sync watcher

What setup does for this item:

- Installs a user LaunchAgent plist at `~/Library/LaunchAgents/com.hermes.codex-menubar-account-sync-watcher.plist`.
- Points launchd at the repo-owned watcher: `scripts/HermesCodexAccountSyncWatcher`.
- Starts it immediately with `launchctl kickstart` and keeps it alive with launchd.
- Writes logs under `~/Library/Logs/Hermes/`.

Install fields:

- **Enabled:** `yes`
- **Kind:** `launchagent`
- **Launchd Label:** `com.hermes.codex-menubar-account-sync-watcher`
- **Installer:** `scripts/install_codex_menubar_sync_watcher.py`
- **Verify:** `launchctl print gui/{uid}/com.hermes.codex-menubar-account-sync-watcher`
