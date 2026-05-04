---
name: cli
description: "Skill for the Cli area of hermes-agent. 115 symbols across 14 files."
---

# Cli

115 symbols | 14 files | Cohesion: 90%

## When to Use

- Working with code in `tests/`
- Understanding how test_focus_topic_extracted_and_passed, test_no_focus_topic_when_bare_command, test_empty_focus_after_command_treated_as_none work
- Modifying cli-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/cli/test_resume_display.py` | _make_cli, _simple_history, _tool_call_history, _capture_display, test_simple_history_shows_user_and_assistant (+27) |
| `tests/cli/test_reasoning_command.py` | _build_msg, _make_agent, test_single_think_block_extracted, test_multiple_think_blocks_extracted, test_no_think_blocks_no_reasoning (+7) |
| `tests/cli/test_cli_status_bar.py` | _make_cli, _attach_agent, test_build_status_bar_text_for_wide_terminal, test_build_status_bar_text_no_cost_in_status_bar, test_build_status_bar_text_collapses_for_narrow_terminal (+7) |
| `tests/cli/test_fast_command.py` | _import_cli, _make_cli, test_no_args_shows_status, test_no_args_shows_fast_when_enabled, test_normal_argument_clears_service_tier (+3) |
| `tests/cli/test_busy_input_mode_command.py` | _import_cli, test_no_args_shows_status, test_interrupt_argument_sets_interrupt_mode_and_saves, test_invalid_argument_prints_usage, _make_cli (+3) |
| `tests/cli/test_worktree.py` | _setup_worktree, _cleanup_worktree, test_clean_worktree_removed, test_dirty_worktree_cleaned_when_no_unpushed, test_worktree_with_unpushed_commits_kept (+2) |
| `tests/cli/test_personality_none.py` | _make_event, _make_runner, test_none_clears_ephemeral_prompt, test_default_clears_ephemeral_prompt, test_list_includes_none (+2) |
| `tests/cli/test_compress_focus.py` | _make_history, test_focus_topic_extracted_and_passed, test_no_focus_topic_when_bare_command, test_empty_focus_after_command_treated_as_none, test_focus_topic_printed_in_compression_banner (+1) |
| `tests/cli/test_cli_skin_integration.py` | _make_cli_stub, test_default_prompt_fragments_use_default_symbol, test_ares_prompt_fragments_use_skin_symbol, test_secret_prompt_fragments_preserve_secret_state, test_build_tui_style_dict_uses_skin_overrides (+1) |
| `tests/cli/test_quick_commands.py` | _printed_plain, _make_cli, test_exec_command_runs_and_prints_output, test_exec_command_uses_chat_console_when_tui_is_live, test_quick_command_takes_priority_over_skill_commands |

## Entry Points

Start here when exploring this area:

- **`test_focus_topic_extracted_and_passed`** (Function) — `tests/cli/test_compress_focus.py:19`
- **`test_no_focus_topic_when_bare_command`** (Function) — `tests/cli/test_compress_focus.py:47`
- **`test_empty_focus_after_command_treated_as_none`** (Function) — `tests/cli/test_compress_focus.py:65`
- **`test_focus_topic_printed_in_compression_banner`** (Function) — `tests/cli/test_compress_focus.py:83`
- **`test_no_focus_prints_standard_banner`** (Function) — `tests/cli/test_compress_focus.py:101`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_focus_topic_extracted_and_passed` | Function | `tests/cli/test_compress_focus.py` | 19 |
| `test_no_focus_topic_when_bare_command` | Function | `tests/cli/test_compress_focus.py` | 47 |
| `test_empty_focus_after_command_treated_as_none` | Function | `tests/cli/test_compress_focus.py` | 65 |
| `test_focus_topic_printed_in_compression_banner` | Function | `tests/cli/test_compress_focus.py` | 83 |
| `test_no_focus_prints_standard_banner` | Function | `tests/cli/test_compress_focus.py` | 101 |
| `test_manual_compress_reports_noop_without_success_banner` | Function | `tests/cli/test_manual_compress.py` | 16 |
| `test_manual_compress_explains_when_token_estimate_rises` | Function | `tests/cli/test_manual_compress.py` | 40 |
| `test_manual_compress_syncs_session_id_after_split` | Function | `tests/cli/test_manual_compress.py` | 72 |
| `test_manual_compress_no_sync_when_session_id_unchanged` | Function | `tests/cli/test_manual_compress.py` | 113 |
| `test_simple_history_shows_user_and_assistant` | Method | `tests/cli/test_resume_display.py` | 128 |
| `test_system_messages_hidden` | Method | `tests/cli/test_resume_display.py` | 139 |
| `test_tool_messages_hidden` | Method | `tests/cli/test_resume_display.py` | 146 |
| `test_tool_calls_shown_as_summary` | Method | `tests/cli/test_resume_display.py` | 155 |
| `test_long_user_message_truncated` | Method | `tests/cli/test_resume_display.py` | 164 |
| `test_long_assistant_message_truncated` | Method | `tests/cli/test_resume_display.py` | 181 |
| `test_multiline_assistant_truncated` | Method | `tests/cli/test_resume_display.py` | 198 |
| `test_last_assistant_response_shown_in_full` | Method | `tests/cli/test_resume_display.py` | 217 |
| `test_last_assistant_multiline_shown_in_full` | Method | `tests/cli/test_resume_display.py` | 232 |
| `test_large_history_shows_truncation_indicator` | Method | `tests/cli/test_resume_display.py` | 247 |
| `test_multimodal_content_handled` | Method | `tests/cli/test_resume_display.py` | 257 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Hermes_cli | 5 calls |
| Tests | 5 calls |

## How to Explore

1. `gitnexus_context({name: "test_focus_topic_extracted_and_passed"})` — see callers and callees
2. `gitnexus_query({query: "cli"})` — find related execution flows
3. Read key files listed above for implementation details
