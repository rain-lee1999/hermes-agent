---
name: tests
description: "Skill for the Tests area of hermes-agent. 246 symbols across 42 files."
---

# Tests

246 symbols | 42 files | Cohesion: 70%

## When to Use

- Working with code in `tests/`
- Understanding how make_adapter, make_ctx, encode_conn_msg work
- Modifying tests-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/test_yuanbao_pipeline.py` | make_adapter, make_ctx, test_new_message_passes, test_duplicate_stops_pipeline, test_self_message_stops (+20) |
| `tests/test_yuanbao_proto.py` | test_basic_round_trip, test_empty_data, test_all_cmd_types, test_large_seq_no, test_full_round_trip (+15) |
| `tests/test_hermes_logging.py` | test_passes_matching_prefix, test_passes_nested_matching_prefix, test_blocks_non_matching, test_multiple_prefixes, test_idempotent_no_duplicate_handlers (+13) |
| `tests/test_model_tools_async_bridge.py` | _get_current_loop, test_loop_not_closed_after_run_async, test_same_loop_reused_across_calls, test_cached_transport_survives_between_calls, _run_on_worker (+9) |
| `tests/test_plugin_skills.py` | _setup_bundle, test_banner_present, test_banner_lists_siblings_not_self, test_single_skill_no_sibling_line, test_original_content_preserved (+8) |
| `mcp_serve.py` | _get_sessions_dir, _load_sessions_index, _load_channel_directory, EventBridge, _poll_once (+7) |
| `tests/test_mcp_serve.py` | _create_test_db, test_poll_detects_new_messages, test_poll_skips_when_unchanged, test_poll_detects_new_message_after_db_write, test_enqueue_and_poll (+7) |
| `tests/test_minimax_oauth.py` | test_request_user_code_happy_path, test_request_user_code_state_mismatch_raises, test_request_user_code_non_200_raises, _make_httpx_response, test_poll_token_pending_then_success (+6) |
| `tests/test_yuanbao_markdown.py` | test_code_fence_not_split, test_code_fence_200_lines_not_cut, test_code_block_200_lines_not_broken, test_fence_not_broken, test_mixed_content (+5) |
| `gateway/platforms/yuanbao_proto.py` | _dbg, encode_conn_msg, decode_conn_msg, encode_send_c2c_message, encode_send_group_message (+4) |

## Entry Points

Start here when exploring this area:

- **`make_adapter`** (Function) — `tests/test_yuanbao_pipeline.py:64`
- **`make_ctx`** (Function) — `tests/test_yuanbao_pipeline.py:72`
- **`encode_conn_msg`** (Function) — `gateway/platforms/yuanbao_proto.py:334`
- **`decode_conn_msg`** (Function) — `gateway/platforms/yuanbao_proto.py:360`
- **`encode_send_c2c_message`** (Function) — `gateway/platforms/yuanbao_proto.py:807`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `EventBridge` | Class | `mcp_serve.py` | 184 |
| `PluginManager` | Class | `hermes_cli/plugins.py` | 601 |
| `make_adapter` | Function | `tests/test_yuanbao_pipeline.py` | 64 |
| `make_ctx` | Function | `tests/test_yuanbao_pipeline.py` | 72 |
| `encode_conn_msg` | Function | `gateway/platforms/yuanbao_proto.py` | 334 |
| `decode_conn_msg` | Function | `gateway/platforms/yuanbao_proto.py` | 360 |
| `encode_send_c2c_message` | Function | `gateway/platforms/yuanbao_proto.py` | 807 |
| `encode_send_group_message` | Function | `gateway/platforms/yuanbao_proto.py` | 856 |
| `channels_list` | Function | `mcp_serve.py` | 739 |
| `detect_local_server_type` | Function | `agent/model_metadata.py` | 395 |
| `query_ollama_num_ctx` | Function | `agent/model_metadata.py` | 895 |
| `atomic_replace` | Function | `utils.py` | 60 |
| `test_atomic_replace_preserves_symlink` | Function | `tests/test_atomic_replace_symlinks.py` | 39 |
| `test_atomic_replace_regular_file` | Function | `tests/test_atomic_replace_symlinks.py` | 55 |
| `test_atomic_replace_first_time_create` | Function | `tests/test_atomic_replace_symlinks.py` | 67 |
| `test_atomic_replace_accepts_pathlike_and_str` | Function | `tests/test_atomic_replace_symlinks.py` | 78 |
| `test_atomic_replace_broken_symlink_creates_target` | Function | `tests/test_atomic_replace_symlinks.py` | 143 |
| `set_active_skin` | Function | `hermes_cli/skin_engine.py` | 749 |
| `get_tool_definitions` | Function | `model_tools.py` | 270 |
| `is_container` | Function | `hermes_constants.py` | 195 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Rollout_and_score_eval → _snapshot_state` | cross_community | 8 |
| `Recover_from_checkpoint → Atomic_replace` | cross_community | 7 |
| `Collect_trajectory → _snapshot_state` | cross_community | 7 |
| `Collect_trajectory → Get_registered_toolset_aliases` | cross_community | 7 |
| `Collect_trajectory → Get_toolset_alias_target` | cross_community | 7 |
| `Rollout_and_score_eval → Get_registered_toolset_aliases` | cross_community | 7 |
| `Rollout_and_score_eval → Get_toolset_alias_target` | cross_community | 7 |
| `Collect_trajectory → _check_fn_cached` | cross_community | 6 |
| `Collect_trajectory → Is_registered` | cross_community | 6 |
| `Rollout_and_score_eval → _check_fn_cached` | cross_community | 6 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Platforms | 33 calls |
| Hermes_cli | 26 calls |
| Tools | 17 calls |
| Agent | 3 calls |
| Gateway | 2 calls |
| Cluster_29 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "make_adapter"})` — see callers and callees
2. `gitnexus_query({query: "tests"})` — find related execution flows
3. Read key files listed above for implementation details
