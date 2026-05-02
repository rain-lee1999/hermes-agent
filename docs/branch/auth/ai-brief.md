---
branch: auth
purpose: macOS 登录项安装 + Codex Menubar 账号顺序同步
read_first: README.md
spec: null
plan: null
primary_files:
  - setup-hermes.sh
  - scripts/install_macos_login_items.sh
  - scripts/macos-login-items.md
  - scripts/install_codex_menubar_sync_watcher.py
  - scripts/HermesCodexAccountSyncWatcher
  - scripts/reorder_codex_by_menubar_quota.py
  - tests/scripts/test_setup_hermes_launchagent_install.py
---

# auth AI brief

## One-line summary

This branch makes `./setup-hermes.sh` install and start the repo-owned macOS LaunchAgent that keeps Codex Menubar account order in sync with Hermes auth, using a Markdown manifest as the install source of truth.

## Must-know concepts

- `scripts/macos-login-items.md`: source of truth for macOS background items.
- `Launchd Label`: stable machine identifier; `Item` is only display text.
- `scripts/install_macos_login_items.sh`: thin helper invoked by setup; no-op off macOS.
- `scripts/HermesCodexAccountSyncWatcher`: long-running watcher that keeps Menubar-derived order fresh.
- `scripts/install_codex_menubar_sync_watcher.py`: LaunchAgent installer for the watcher.
- `scripts/reorder_codex_by_menubar_quota.py`: one-shot reorder/sync logic.

## Before vs after

### Before

- `setup-hermes.sh` did not centrally manage macOS login-item installation.
- LaunchAgent install/start logic was easier to miss or duplicate.
- Menubar sync and setup bootstrap were not connected by one reliable install path.

### After

- `setup-hermes.sh` delegates to a shared helper at the end of setup.
- The helper parses `scripts/macos-login-items.md` and installs items in order.
- The watcher is launched via `launchctl` and can be verified with `launchctl print gui/{uid}/com.hermes.codex-menubar-account-sync-watcher`.

## Invariants to preserve

1. `setup-hermes.sh` stays a thin entry point; new macOS items go in the manifest/helper.
2. `Launchd Label` remains the stable identifier used by tests and verification.
3. Menubar order syncing should preserve the persisted ranking order; do not re-sort independently.

## Where to look in code

- `setup-hermes.sh` — final setup hook into the helper.
- `scripts/install_macos_login_items.sh` — manifest parser and installer dispatcher.
- `scripts/macos-login-items.md` — editable source of truth for login items.
- `scripts/install_codex_menubar_sync_watcher.py` — LaunchAgent plist installer.
- `scripts/HermesCodexAccountSyncWatcher` — long-running watcher entry point.
- `scripts/reorder_codex_by_menubar_quota.py` — one-shot sync/reorder logic.
- `tests/scripts/test_setup_hermes_launchagent_install.py` — setup + install regression coverage.

## Fast mental model

Think of this branch as “setup bootstraps the watcher, the watcher keeps Menubar-derived order fresh, and the auth layer consumes that order.” The launchd pieces make it survive process exits; the manifest makes the install path extensible.

## Verification

- `git rev-parse --show-toplevel`: `/Users/rain/dev/-github/hermes-agent-auth`
- `git branch --show-current`: `auth`
- `git log --oneline --decorate --graph upstream/main..HEAD --max-count=20`: branch currently has one unique commit, `386a5c5c8`
- `date +%F`: `2026-05-02`
- Earlier code verification already reported passing for `bash -n setup-hermes.sh`, `python3 -m py_compile ...`, and targeted pytest on the setup/watcher/quota tests; not rerun during this docs pass.

## Future work usually looks like

- Add another macOS background item by appending a new `## Item:` section to `scripts/macos-login-items.md`.
- Extend installer parsing/validation for another login-item type.
- Tweak watcher/reorder behavior when Menubar snapshot format or auth-state handling changes.