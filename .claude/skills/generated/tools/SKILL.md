---
name: tools
description: "Skill for the Tools area of hermes-agent. 2208 symbols across 217 files."
---

# Tools

2208 symbols | 217 files | Cohesion: 67%

## When to Use

- Working with code in `tests/`
- Understanding how writer, skill_view, has_traversal_component work
- Modifying tools-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tools/skills_hub.py` | _featured_skills, _fetch_detail_page, _normalize_tags, _query_terms, _search_score (+101) |
| `tests/tools/test_delegate.py` | test_no_goal_or_tasks, test_task_missing_goal, test_batch_mode, test_batch_capped_at_3, test_active_children_tracking (+83) |
| `tests/tools/test_mcp_tool.py` | test_overwrite_same_toolset_no_warning, test_toolset_resolves_live_from_registry, test_mcp_tools_resolve_through_server_aliases, test_server_toolset_skips_builtin_collision, test_shutdown_deregisters_registered_tools (+80) |
| `tools/mcp_tool.py` | _run_on_mcp_loop, _convert_mcp_schema, _register_server_tools, _discover_and_register_server, _sanitize_error (+60) |
| `tests/tools/test_send_message_tool.py` | _install_telegram_mock, test_sends_text_then_photo_for_media_tag, test_sends_voice_for_ogg_with_voice_directive, test_sends_audio_for_mp3, test_missing_media_returns_error_without_leaking_raw_tag (+54) |
| `tools/tts_tool.py` | get_env_value, _import_elevenlabs, _import_mistral_client, _import_sounddevice, _import_kittentts (+46) |
| `tools/browser_tool.py` | _reap_orphaned_browser_sessions, _get_session_info, _get_command_timeout, _get_cloud_provider, _is_local_backend (+46) |
| `tests/tools/test_skill_manager_tool.py` | _skill_dir, test_create_skill, test_create_with_category, test_create_duplicate_blocked, test_create_invalid_name (+43) |
| `tests/tools/test_skills_tool.py` | _make_skill, test_view_existing_skill, test_skill_view_applies_template_vars, test_skill_view_applies_inline_shell_when_enabled, test_skill_view_leaves_inline_shell_literal_when_disabled (+36) |
| `tools/terminal_tool.py` | _handle_sudo_failure, _interpret_exit_code, _command_requires_pipe_stdin, _foreground_background_guidance, _resolve_notification_flag_conflict (+33) |

## Entry Points

Start here when exploring this area:

- **`writer`** (Function) — `tests/tools/test_registry.py:489`
- **`skill_view`** (Function) — `tools/skills_tool.py:848`
- **`has_traversal_component`** (Function) — `tools/path_security.py:36`
- **`parse_qualified_name`** (Function) — `agent/skill_utils.py:458`
- **`is_valid_namespace`** (Function) — `agent/skill_utils.py:468`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `writer` | Function | `tests/tools/test_registry.py` | 489 |
| `skill_view` | Function | `tools/skills_tool.py` | 848 |
| `has_traversal_component` | Function | `tools/path_security.py` | 36 |
| `parse_qualified_name` | Function | `agent/skill_utils.py` | 458 |
| `is_valid_namespace` | Function | `agent/skill_utils.py` | 468 |
| `get_toolset` | Function | `toolsets.py` | 505 |
| `resolve_toolset` | Function | `toolsets.py` | 551 |
| `resolve_multiple_toolsets` | Function | `toolsets.py` | 625 |
| `get_all_toolsets` | Function | `toolsets.py` | 670 |
| `get_toolset_names` | Function | `toolsets.py` | 695 |
| `validate_toolset` | Function | `toolsets.py` | 718 |
| `create_custom_toolset` | Function | `toolsets.py` | 738 |
| `get_toolset_info` | Function | `toolsets.py` | 762 |
| `test_kanban_tools_hidden_without_env_var` | Function | `tests/tools/test_kanban_tools.py` | 20 |
| `test_kanban_tools_visible_with_env_var` | Function | `tests/tools/test_kanban_tools.py` | 40 |
| `get_env_value` | Function | `tools/tts_tool.py` | 58 |
| `text_to_speech_tool` | Function | `tools/tts_tool.py` | 1538 |
| `stream_tts_to_speaker` | Function | `tools/tts_tool.py` | 1915 |
| `read_file_tool` | Function | `tools/file_tools.py` | 446 |
| `reset_file_dedup` | Function | `tools/file_tools.py` | 660 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Rollout_and_score_eval → _snapshot_state` | cross_community | 8 |
| `Recover_from_checkpoint → _preserve_file_mode` | cross_community | 7 |
| `Recover_from_checkpoint → Atomic_replace` | cross_community | 7 |
| `Recover_from_checkpoint → _restore_file_mode` | cross_community | 7 |
| `Execute → Get_session_env` | cross_community | 7 |
| `Execute → _get_sudo_password_callback` | cross_community | 7 |
| `Collect_trajectory → _snapshot_state` | cross_community | 7 |
| `Collect_trajectory → Get_registered_toolset_aliases` | cross_community | 7 |
| `Collect_trajectory → Get_toolset_alias_target` | cross_community | 7 |
| `Rollout_and_score_eval → Get_registered_toolset_aliases` | cross_community | 7 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Hermes_cli | 111 calls |
| Agent | 36 calls |
| Gateway | 25 calls |
| Platforms | 20 calls |
| Environments | 14 calls |
| Tests | 8 calls |
| Tui_gateway | 7 calls |
| Cron | 3 calls |

## How to Explore

1. `gitnexus_context({name: "writer"})` — see callers and callees
2. `gitnexus_query({query: "tools"})` — find related execution flows
3. Read key files listed above for implementation details
