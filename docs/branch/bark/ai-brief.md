---
branch: bark
purpose: Default-enable and verify the bark_macos_notify plugin
read_first: README.md
spec: null
plan: null
primary_files:
  - hermes_cli/plugins.py
  - plugins/bark_macos_notify/plugin.yaml
  - plugins/bark_macos_notify/__init__.py
  - tests/plugins/test_bark_macos_notify_plugin.py
  - tests/hermes_cli/test_plugins.py
---

# bark AI brief

## One-line summary

This branch turns `bark_macos_notify` into a bundled plugin that loads by default and actually fires notifications through Hermes hook callbacks.

## Must-know concepts

- Plugin discovery is not the same as plugin enablement.
- `default_enabled` makes a bundled standalone plugin load without a manual allow-list entry.
- `plugins.disabled` still overrides everything.
- Notification delivery is defensive: missing Bark config or missing macOS capabilities should degrade to a no-op, not a crash.
- The important runtime path is `discover -> load -> register(ctx) -> invoke_hook(...)`.

## Before vs after

### Before

- The plugin could exist on disk or in a user profile without being actually active.
- Standalone plugins still depended on explicit config allow-listing.
- There was no end-to-end proof that the notification hook path fired.

### After

- `plugins/bark_macos_notify/plugin.yaml` declares `default_enabled: true`.
- `hermes_cli/plugins.py` honors that flag during discovery/load.
- `plugins/bark_macos_notify/__init__.py` registers `pre_tool_call`, `post_llm_call`, `on_session_finalize`, and `on_session_reset`.
- Tests prove that PluginManager loads the plugin without an allow-list and that `post_llm_call` can trigger the notification path.

## Invariants to preserve

1. `plugins.disabled` must continue to win over `default_enabled`.
2. Bark/macOS notifications must stay opt-in and fail-soft when configuration or platform support is missing.
3. Hook names and hook registration must stay aligned with Hermes core (`pre_tool_call`, `post_llm_call`, `on_session_finalize`, `on_session_reset`).

## Where to look in code

- `hermes_cli/plugins.py` — discovery, manifest parsing, enablement rules, hook registration.
- `plugins/bark_macos_notify/plugin.yaml` — plugin metadata and default enablement.
- `plugins/bark_macos_notify/__init__.py` — notification logic and `register(ctx)`.
- `tests/plugins/test_bark_macos_notify_plugin.py` — end-to-end plugin discovery/load/invoke coverage.
- `tests/hermes_cli/test_plugins.py` — regression coverage for the wider plugin system.

## Fast mental model

The branch adds a small but important contract change: a bundled notification plugin can now self-declare that it should be active by default. Hermes discovers the manifest, sees `default_enabled: true`, loads the module, calls `register(ctx)`, and the relevant hook callbacks decide whether to send Bark and/or macOS notifications.

## Verification

- `python -m pytest -q tests/plugins/test_bark_macos_notify_plugin.py tests/hermes_cli/test_plugins.py`: passed.
- `mcp_crg_detect_changes_tool` on the three changed files: 0 affected flows reported.

## Future work usually looks like

- Add new notification triggers or refine the filtering logic.
- Document or expand the opt-in environment variables without exposing secrets.
- Add more integration tests if new hooks or delivery channels are introduced.
- If the installation workflow changes, keep the repo branch docs separate from the installed `~/.hermes` profile state.
