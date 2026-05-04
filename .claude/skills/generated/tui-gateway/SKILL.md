---
name: tui-gateway
description: "Skill for the Tui_gateway area of hermes-agent. 118 symbols across 20 files."
---

# Tui_gateway

118 symbols | 20 files | Cohesion: 67%

## When to Use

- Working with code in `tui_gateway/`
- Understanding how get_toolset_for_tool, parse_reasoning_effort, current_transport work
- Modifying tui_gateway-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tui_gateway/server.py` | close, _load_busy_input_mode, _notify_session_boundary, _finalize_session, _get_db (+75) |
| `tests/tui_gateway/test_render.py` | _no_rich, test_render_message_none_without_module, test_render_diff_none_without_module, test_stream_renderer_none_without_module, test_stream_renderer_returns_instance (+4) |
| `tools/approval.py` | enable_session_yolo, disable_session_yolo, is_session_yolo_enabled, load_permanent_allowlist |
| `tui_gateway/ws.py` | write, write_async, _safe_send, handle_ws |
| `tui_gateway/render.py` | render_diff, make_stream_renderer, render_message |
| `tests/tools/test_yolo_mode.py` | test_session_scoped_yolo_only_bypasses_current_session, test_clear_session_removes_session_yolo_state |
| `tests/gateway/test_session_boundary_security_state.py` | test_resume_clears_session_scoped_approval_and_yolo_state, test_clear_session_boundary_security_state_is_scoped |
| `tools/browser_tool.py` | _emergency_cleanup_all_sessions, cleanup_all_browsers |
| `model_tools.py` | get_toolset_for_tool |
| `hermes_constants.py` | parse_reasoning_effort |

## Entry Points

Start here when exploring this area:

- **`get_toolset_for_tool`** (Function) — `model_tools.py:794`
- **`parse_reasoning_effort`** (Function) — `hermes_constants.py:143`
- **`current_transport`** (Function) — `tui_gateway/transport.py:84`
- **`write_json`** (Function) — `tui_gateway/server.py:356`
- **`run`** (Function) — `tui_gateway/server.py:494`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `get_toolset_for_tool` | Function | `model_tools.py` | 794 |
| `parse_reasoning_effort` | Function | `hermes_constants.py` | 143 |
| `current_transport` | Function | `tui_gateway/transport.py` | 84 |
| `write_json` | Function | `tui_gateway/server.py` | 356 |
| `run` | Function | `tui_gateway/server.py` | 494 |
| `resolve_skin` | Function | `tui_gateway/server.py` | 743 |
| `run_after_agent_ready` | Function | `tui_gateway/server.py` | 2799 |
| `main` | Function | `tui_gateway/entry.py` | 159 |
| `set_secret_capture_callback` | Function | `tools/skills_tool.py` | 145 |
| `enable_session_yolo` | Function | `tools/approval.py` | 455 |
| `disable_session_yolo` | Function | `tools/approval.py` | 463 |
| `is_session_yolo_enabled` | Function | `tools/approval.py` | 487 |
| `load_permanent_allowlist` | Function | `tools/approval.py` | 531 |
| `get_available_skills` | Function | `hermes_cli/banner.py` | 99 |
| `estimate_request_tokens_rough` | Function | `agent/model_metadata.py` | 1451 |
| `test_yolo_command_toggles_only_current_session` | Function | `tests/gateway/test_yolo_command.py` | 43 |
| `test_resume_clears_session_scoped_approval_and_yolo_state` | Function | `tests/gateway/test_session_boundary_security_state.py` | 122 |
| `test_clear_session_boundary_security_state_is_scoped` | Function | `tests/gateway/test_session_boundary_security_state.py` | 207 |
| `render_diff` | Function | `tui_gateway/render.py` | 23 |
| `make_stream_renderer` | Function | `tui_gateway/render.py` | 37 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `_ → _is_host_pid_alive` | cross_community | 6 |
| `_ → Strip_ansi` | cross_community | 5 |
| `_ → _get_project_files` | cross_community | 5 |
| `_ → _score_path` | cross_community | 5 |
| `_ → _file_size_label` | cross_community | 5 |
| `_ → _terminate_host_pid` | cross_community | 4 |
| `Run → _err` | cross_community | 4 |
| `_ → _extract_context_word` | cross_community | 3 |
| `_ → _extract_path_word` | cross_community | 3 |
| `Run → Set_session_vars` | cross_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Hermes_cli | 51 calls |
| Tools | 46 calls |
| Agent | 13 calls |
| Gateway | 6 calls |
| Acp_adapter | 1 calls |
| Tests | 1 calls |
| Cron | 1 calls |

## How to Explore

1. `gitnexus_context({name: "get_toolset_for_tool"})` — see callers and callees
2. `gitnexus_query({query: "tui_gateway"})` — find related execution flows
3. Read key files listed above for implementation details
