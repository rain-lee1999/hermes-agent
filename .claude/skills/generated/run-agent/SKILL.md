---
name: run-agent
description: "Skill for the Run_agent area of hermes-agent. 387 symbols across 39 files."
---

# Run_agent

387 symbols | 39 files | Cohesion: 74%

## When to Use

- Working with code in `tests/`
- Understanding how coerce_tool_args, test_normalize_codex_response_preserves_message_status_for_replay, test_normalize_codex_response_reasoning_with_content_is_stop work
- Modifying run_agent-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/run_agent/test_run_agent.py` | _mock_response, _setup_agent, test_stop_finish_reason_returns_response, test_tool_calls_then_stop, test_request_scoped_api_hooks_fire_for_each_api_call (+77) |
| `tests/run_agent/test_run_agent_codex_responses.py` | test_normalize_codex_response_preserves_message_status_for_replay, test_normalize_codex_response_reasoning_with_content_is_stop, _patch_agent_bootstrap, _build_agent, _build_copilot_agent (+37) |
| `tests/run_agent/test_provider_parity.py` | _make_agent, test_user_message_passes_through, test_system_messages_filtered, test_assistant_tool_calls_become_function_call_items, test_tool_results_become_function_call_output (+21) |
| `tests/run_agent/test_primary_runtime_restore.py` | _make_tool_defs, _make_agent, _make_transport_error, test_recovers_on_read_timeout, test_recovers_on_connect_timeout (+21) |
| `tests/run_agent/test_streaming.py` | _make_stream_chunk, test_tool_call_extra_content_preserved, test_tool_only_does_not_fire_callback, _stalling_stream, _gen (+13) |
| `tests/run_agent/test_tool_arg_coercion.py` | _mock_schema, test_coerces_integer_arg, test_coerces_boolean_arg, test_coerces_number_arg, test_leaves_string_args_alone (+10) |
| `tests/run_agent/test_fallback_model.py` | _make_agent, _mock_resolve, test_activates_openrouter_fallback, test_activates_zai_fallback, test_fallback_uses_resolved_normalized_model (+10) |
| `tests/run_agent/test_tool_call_guardrail_runtime.py` | _mock_tool_call, _mock_response, _make_agent, _seed_exact_failures, _hard_stop_config (+7) |
| `tests/run_agent/test_agent_loop.py` | make_tool_response, test_tool_call_then_text, test_max_turns_reached, test_unknown_tool_name, test_memory_tool_blocked (+7) |
| `agent/codex_responses_adapter.py` | _chat_content_to_responses_parts, _responses_tools, _chat_messages_to_responses_input, _deterministic_call_id, _split_responses_tool_id (+4) |

## Entry Points

Start here when exploring this area:

- **`coerce_tool_args`** (Function) — `model_tools.py:502`
- **`test_normalize_codex_response_preserves_message_status_for_replay`** (Function) — `tests/run_agent/test_run_agent_codex_responses.py:945`
- **`test_normalize_codex_response_reasoning_with_content_is_stop`** (Function) — `tests/run_agent/test_run_agent_codex_responses.py:1445`
- **`test_default_sequential_path_warns_repeated_exact_failure_without_blocking_execution`** (Function) — `tests/run_agent/test_tool_call_guardrail_runtime.py:88`
- **`test_config_enabled_hard_stop_blocks_repeated_exact_failure_before_execution`** (Function) — `tests/run_agent/test_tool_call_guardrail_runtime.py:114`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `coerce_tool_args` | Function | `model_tools.py` | 502 |
| `test_normalize_codex_response_preserves_message_status_for_replay` | Function | `tests/run_agent/test_run_agent_codex_responses.py` | 945 |
| `test_normalize_codex_response_reasoning_with_content_is_stop` | Function | `tests/run_agent/test_run_agent_codex_responses.py` | 1445 |
| `test_default_sequential_path_warns_repeated_exact_failure_without_blocking_execution` | Function | `tests/run_agent/test_tool_call_guardrail_runtime.py` | 88 |
| `test_config_enabled_hard_stop_blocks_repeated_exact_failure_before_execution` | Function | `tests/run_agent/test_tool_call_guardrail_runtime.py` | 114 |
| `test_sequential_after_call_appends_guidance_to_tool_result_without_extra_messages` | Function | `tests/run_agent/test_tool_call_guardrail_runtime.py` | 138 |
| `test_config_enabled_hard_stop_concurrent_path_does_not_submit_blocked_calls_and_preserves_result_order` | Function | `tests/run_agent/test_tool_call_guardrail_runtime.py` | 155 |
| `test_plugin_pre_tool_block_wins_without_counting_as_toolguard_block` | Function | `tests/run_agent/test_tool_call_guardrail_runtime.py` | 191 |
| `test_default_run_conversation_warns_without_guardrail_halt` | Function | `tests/run_agent/test_tool_call_guardrail_runtime.py` | 209 |
| `test_config_enabled_hard_stop_run_conversation_returns_controlled_guardrail_halt_without_top_level_error` | Function | `tests/run_agent/test_tool_call_guardrail_runtime.py` | 239 |
| `make_tool_response` | Function | `tests/run_agent/test_agent_loop.py` | 102 |
| `test_chat_messages_to_responses_input_uses_call_id_for_function_call` | Function | `tests/run_agent/test_run_agent_codex_responses.py` | 726 |
| `test_chat_messages_to_responses_input_accepts_call_pipe_fc_ids` | Function | `tests/run_agent/test_run_agent_codex_responses.py` | 755 |
| `test_normalize_codex_response_detects_leaked_tool_call_text` | Function | `tests/run_agent/test_run_agent_codex_responses.py` | 972 |
| `test_normalize_codex_response_ignores_tool_call_text_when_real_tool_call_present` | Function | `tests/run_agent/test_run_agent_codex_responses.py` | 1012 |
| `test_normalize_codex_response_no_leak_passes_through` | Function | `tests/run_agent/test_run_agent_codex_responses.py` | 1050 |
| `test_chat_messages_to_responses_input_reasoning_only_has_following_item` | Function | `tests/run_agent/test_run_agent_codex_responses.py` | 1536 |
| `test_chat_messages_to_responses_input_deduplicates_reasoning_ids` | Function | `tests/run_agent/test_run_agent_codex_responses.py` | 1707 |
| `get_session_messages` | Function | `hermes_cli/web_server.py` | 2177 |
| `test_codex_message_item_status_survives_conversion_and_preflight` | Function | `tests/run_agent/test_run_agent_codex_responses.py` | 1567 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Cmd_sessions → _decode_content` | cross_community | 4 |
| `Cmd_sessions → Search_sessions` | cross_community | 3 |
| `Collect_trajectory → _get_managed_state` | cross_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Tools | 11 calls |
| Gateway | 5 calls |
| Agent | 4 calls |
| Hermes_cli | 2 calls |
| Cluster_21 | 2 calls |
| Tests | 1 calls |

## How to Explore

1. `gitnexus_context({name: "coerce_tool_args"})` — see callers and callees
2. `gitnexus_query({query: "run_agent"})` — find related execution flows
3. Read key files listed above for implementation details
