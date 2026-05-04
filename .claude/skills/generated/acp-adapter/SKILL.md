---
name: acp-adapter
description: "Skill for the Acp_adapter area of hermes-agent. 62 symbols across 13 files."
---

# Acp_adapter

62 symbols | 13 files | Cohesion: 77%

## When to Use

- Working with code in `acp_adapter/`
- Understanding how make_agent_and_state, detect_provider, has_provider work
- Modifying acp_adapter-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `acp_adapter/session.py` | _translate_acp_cwd, _register_task_cwd, create_session, get_session, fork_session (+13) |
| `acp_adapter/server.py` | _encode_model_choice, _build_model_state, _register_session_mcp_servers, _replay_session_history, new_session (+11) |
| `acp_adapter/tools.py` | get_tool_kind, _parse_unified_diff_content, _flush, _build_tool_complete_content, build_tool_complete (+5) |
| `acp_adapter/events.py` | make_thinking_cb, make_message_cb, _send_update, _tool_progress, _step (+2) |
| `acp_adapter/auth.py` | detect_provider, has_provider |
| `tests/acp/test_server.py` | test_set_session_model_accepts_provider_prefixed_choice, test_model_switch_uses_requested_provider |
| `tests/acp_adapter/test_acp_commands.py` | make_agent_and_state |
| `tests/acp/test_session.py` | test_restore_preserves_persisted_provider_snapshot |
| `acp_adapter/permissions.py` | make_approval_callback |
| `agent/title_generator.py` | maybe_auto_title |

## Entry Points

Start here when exploring this area:

- **`make_agent_and_state`** (Function) — `tests/acp_adapter/test_acp_commands.py:58`
- **`detect_provider`** (Function) — `acp_adapter/auth.py:7`
- **`has_provider`** (Function) — `acp_adapter/auth.py:21`
- **`make_approval_callback`** (Function) — `acp_adapter/permissions.py:25`
- **`make_thinking_cb`** (Function) — `acp_adapter/events.py:107`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `make_agent_and_state` | Function | `tests/acp_adapter/test_acp_commands.py` | 58 |
| `detect_provider` | Function | `acp_adapter/auth.py` | 7 |
| `has_provider` | Function | `acp_adapter/auth.py` | 21 |
| `make_approval_callback` | Function | `acp_adapter/permissions.py` | 25 |
| `make_thinking_cb` | Function | `acp_adapter/events.py` | 107 |
| `make_message_cb` | Function | `acp_adapter/events.py` | 180 |
| `maybe_auto_title` | Function | `agent/title_generator.py` | 125 |
| `parse_model_input` | Function | `hermes_cli/models.py` | 1410 |
| `get_tool_kind` | Function | `acp_adapter/tools.py` | 53 |
| `build_tool_complete` | Function | `acp_adapter/tools.py` | 340 |
| `make_tool_call_id` | Function | `acp_adapter/tools.py` | 58 |
| `build_tool_title` | Function | `acp_adapter/tools.py` | 63 |
| `build_tool_start` | Function | `acp_adapter/tools.py` | 268 |
| `extract_locations` | Function | `acp_adapter/tools.py` | 369 |
| `make_tool_progress_cb` | Function | `acp_adapter/events.py` | 46 |
| `make_step_cb` | Function | `acp_adapter/events.py` | 127 |
| `create_session` | Method | `acp_adapter/session.py` | 209 |
| `get_session` | Method | `acp_adapter/session.py` | 230 |
| `fork_session` | Method | `acp_adapter/session.py` | 252 |
| `update_cwd` | Method | `acp_adapter/session.py` | 356 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Hermes_cli | 9 calls |
| Tests | 3 calls |
| Tools | 2 calls |
| Agent | 2 calls |
| Terminalbench_2 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "make_agent_and_state"})` — see callers and callees
2. `gitnexus_query({query: "acp_adapter"})` — find related execution flows
3. Read key files listed above for implementation details
