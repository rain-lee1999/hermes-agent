---
name: plugins
description: "Skill for the Plugins area of hermes-agent. 68 symbols across 15 files."
---

# Plugins

68 symbols | 15 files | Cohesion: 74%

## When to Use

- Working with code in `tests/`
- Understanding how test_server_ensure_token_generates_and_persists, test_server_get_token_is_idempotent, test_server_handle_request_rejects_bad_token work
- Modifying plugins-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/plugins/test_google_meet_node.py` | test_server_ensure_token_generates_and_persists, test_server_get_token_is_idempotent, test_server_handle_request_rejects_bad_token, test_server_handle_request_ping, test_server_handle_request_status_dispatches_to_pm (+15) |
| `tests/plugins/test_retaindb_plugin.py` | test_enqueue_persists_to_sqlite, test_flush_records_error_on_failure, test_crash_recovery_replays_pending, _make_initialized_provider, test_sync_turn_enqueues (+5) |
| `plugins/memory/retaindb/__init__.py` | enqueue, shutdown, initialize, sync_turn, on_memory_write (+1) |
| `tests/plugins/test_google_meet_realtime.py` | _install_fake_websockets, test_connect_sends_session_update_with_voice_and_instructions, test_speak_sends_create_and_response_and_writes_audio, test_speak_raises_on_error_frame, test_close_is_idempotent_and_closes_ws |
| `plugins/google_meet/realtime/openai_client.py` | connect, close, speak, cancel_response, _send_json |
| `tests/plugins/test_google_meet_plugin.py` | test_meet_join_routes_to_registered_node, test_meet_join_auto_node_selects_sole_registered, test_meet_join_auto_node_ambiguous_returns_error, test_bot_state_dedupes_captions_and_flushes_status, test_bot_state_ignores_blank_text |
| `web/src/plugins/registry.ts` | getPluginComponent, _notify, notifyPluginRegistry, setPluginLoadError, onPluginRegistered |
| `plugins/google_meet/node/server.py` | ensure_token, get_token, _handle_request |
| `web/src/plugins/usePlugins.ts` | usePlugins, resolvePlugins |
| `web/src/plugins/PluginPage.tsx` | Component, loadError |

## Entry Points

Start here when exploring this area:

- **`test_server_ensure_token_generates_and_persists`** (Function) — `tests/plugins/test_google_meet_node.py:229`
- **`test_server_get_token_is_idempotent`** (Function) — `tests/plugins/test_google_meet_node.py:247`
- **`test_server_handle_request_rejects_bad_token`** (Function) — `tests/plugins/test_google_meet_node.py:258`
- **`test_server_handle_request_ping`** (Function) — `tests/plugins/test_google_meet_node.py:270`
- **`test_server_handle_request_status_dispatches_to_pm`** (Function) — `tests/plugins/test_google_meet_node.py:283`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_server_ensure_token_generates_and_persists` | Function | `tests/plugins/test_google_meet_node.py` | 229 |
| `test_server_get_token_is_idempotent` | Function | `tests/plugins/test_google_meet_node.py` | 247 |
| `test_server_handle_request_rejects_bad_token` | Function | `tests/plugins/test_google_meet_node.py` | 258 |
| `test_server_handle_request_ping` | Function | `tests/plugins/test_google_meet_node.py` | 270 |
| `test_server_handle_request_status_dispatches_to_pm` | Function | `tests/plugins/test_google_meet_node.py` | 283 |
| `test_server_handle_request_start_bot_dispatches` | Function | `tests/plugins/test_google_meet_node.py` | 300 |
| `test_server_handle_request_start_bot_missing_url` | Function | `tests/plugins/test_google_meet_node.py` | 328 |
| `test_server_handle_request_stop_dispatches` | Function | `tests/plugins/test_google_meet_node.py` | 340 |
| `test_server_handle_request_transcript` | Function | `tests/plugins/test_google_meet_node.py` | 361 |
| `test_server_handle_request_say_enqueues_when_active` | Function | `tests/plugins/test_google_meet_node.py` | 383 |
| `test_server_handle_request_say_without_active_still_ok` | Function | `tests/plugins/test_google_meet_node.py` | 405 |
| `test_server_handle_request_wraps_pm_exceptions` | Function | `tests/plugins/test_google_meet_node.py` | 421 |
| `test_connect_sends_session_update_with_voice_and_instructions` | Function | `tests/plugins/test_google_meet_realtime.py` | 88 |
| `test_speak_sends_create_and_response_and_writes_audio` | Function | `tests/plugins/test_google_meet_realtime.py` | 127 |
| `test_speak_raises_on_error_frame` | Function | `tests/plugins/test_google_meet_realtime.py` | 167 |
| `test_close_is_idempotent_and_closes_ws` | Function | `tests/plugins/test_google_meet_realtime.py` | 190 |
| `test_meet_join_routes_to_registered_node` | Function | `tests/plugins/test_google_meet_plugin.py` | 504 |
| `test_meet_join_auto_node_selects_sole_registered` | Function | `tests/plugins/test_google_meet_plugin.py` | 538 |
| `test_meet_join_auto_node_ambiguous_returns_error` | Function | `tests/plugins/test_google_meet_plugin.py` | 556 |
| `handle_meet_join` | Function | `plugins/google_meet/tools.py` | 235 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `App → _notify` | cross_community | 4 |
| `App → GetPluginComponent` | cross_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Node | 14 calls |
| Google_meet | 4 calls |
| Retaindb | 1 calls |
| Hermes_cli | 1 calls |

## How to Explore

1. `gitnexus_context({name: "test_server_ensure_token_generates_and_persists"})` — see callers and callees
2. `gitnexus_query({query: "plugins"})` — find related execution flows
3. Read key files listed above for implementation details
