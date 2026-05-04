---
name: gateway
description: "Skill for the Gateway area of hermes-agent. 1928 symbols across 186 files."
---

# Gateway

1928 symbols | 186 files | Cohesion: 78%

## When to Use

- Working with code in `tests/`
- Understanding how test_search_sessions_exposes_last_active_column, test_whatsapp_lid_user_matches_phone_allowlist_via_session_mapping, test_star_wildcard_in_allowlist_authorizes_any_user work
- Modifying gateway-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/gateway/test_stream_consumer.py` | test_stream_with_media_tag, test_segment_break_creates_new_message, test_segment_break_no_text_before, test_segment_break_removes_cursor, test_multiple_segment_breaks (+50) |
| `tests/gateway/test_voice_command.py` | _make_receiver, _fill_buffer, test_known_ssrc_returns_completed, test_known_ssrc_short_buffer_ignored, test_known_ssrc_recent_audio_waits (+45) |
| `tests/gateway/test_feishu.py` | _make_refs, test_strips_leading_self, test_strips_consecutive_leading_self, test_stops_at_first_non_self_token, test_preserves_mid_text_self (+41) |
| `tests/gateway/test_signal.py` | _make_signal_adapter, _stub_rpc, test_fetch_attachment_uses_id_parameter, test_fetch_attachment_returns_none_on_empty, test_fetch_attachment_handles_dict_response (+34) |
| `tests/gateway/test_media_download_retry.py` | _make_http_status_error, test_success_on_first_attempt, run, test_retries_on_429_then_succeeds, test_non_retryable_4xx_raises_immediately (+33) |
| `tests/gateway/test_channel_directory.py` | _setup, test_exact_match, test_case_insensitive, test_guild_qualified_match, test_prefix_match_unambiguous (+30) |
| `gateway/status.py` | _get_pid_path, _get_gateway_lock_path, _looks_like_gateway_process, _read_pid_record, _read_gateway_lock_record (+27) |
| `gateway/session.py` | rewrite_transcript, _now, _ensure_loaded_locked, _save, _generate_session_key (+25) |
| `tests/gateway/test_signal_format.py` | _m2s, _find_style, test_snake_case_not_italic, test_multiple_snake_case, test_snake_case_path (+25) |
| `tests/gateway/test_unauthorized_dm_behavior.py` | _clear_auth_env, _make_event, _make_runner, test_whatsapp_lid_user_matches_phone_allowlist_via_session_mapping, test_star_wildcard_in_allowlist_authorizes_any_user (+24) |

## Entry Points

Start here when exploring this area:

- **`test_search_sessions_exposes_last_active_column`** (Function) — `tests/hermes_cli/test_resolve_last_session.py:48`
- **`test_whatsapp_lid_user_matches_phone_allowlist_via_session_mapping`** (Function) — `tests/gateway/test_unauthorized_dm_behavior.py:76`
- **`test_star_wildcard_in_allowlist_authorizes_any_user`** (Function) — `tests/gateway/test_unauthorized_dm_behavior.py:102`
- **`test_star_wildcard_works_for_any_platform`** (Function) — `tests/gateway/test_unauthorized_dm_behavior.py:122`
- **`test_qq_group_allowlist_authorizes_group_chat_without_user_allowlist`** (Function) — `tests/gateway/test_unauthorized_dm_behavior.py:142`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `test_search_sessions_exposes_last_active_column` | Function | `tests/hermes_cli/test_resolve_last_session.py` | 48 |
| `test_whatsapp_lid_user_matches_phone_allowlist_via_session_mapping` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 76 |
| `test_star_wildcard_in_allowlist_authorizes_any_user` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 102 |
| `test_star_wildcard_works_for_any_platform` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 122 |
| `test_qq_group_allowlist_authorizes_group_chat_without_user_allowlist` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 142 |
| `test_qq_group_allowlist_does_not_authorize_other_groups` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 162 |
| `test_telegram_group_user_allowlist_authorizes_forum_sender_without_dm_allowlist` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 182 |
| `test_telegram_group_user_allowlist_rejects_other_senders` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 201 |
| `test_telegram_group_user_allowlist_wildcard_authorizes_any_sender` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 220 |
| `test_telegram_group_user_allowlist_does_not_authorize_dms` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 239 |
| `test_telegram_group_chat_allowlist_authorizes_group_chat_without_user_allowlist` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 258 |
| `test_telegram_group_users_legacy_chat_ids_still_authorize` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 278 |
| `test_telegram_group_users_legacy_does_not_cross_chats` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 304 |
| `test_telegram_group_users_mixed_sender_and_legacy_chat` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 325 |
| `test_unauthorized_dm_pairs_by_default` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 357 |
| `test_unauthorized_whatsapp_dm_can_be_ignored` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 384 |
| `test_rate_limited_user_gets_no_response` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 410 |
| `test_rejection_message_records_rate_limit` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 433 |
| `test_global_ignore_suppresses_pairing_reply` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 460 |
| `test_signal_with_allowlist_ignores_unauthorized_dm` | Function | `tests/gateway/test_unauthorized_dm_behavior.py` | 487 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Run_uninstall → Get_hermes_home` | cross_community | 8 |
| `Execute → Get_session_env` | cross_community | 7 |
| `Run_uninstall → _try_acquire_file_lock` | cross_community | 7 |
| `Run_uninstall → _release_file_lock` | cross_community | 7 |
| `Cmd_profile → Get_hermes_home` | cross_community | 6 |
| `Cmd_profile → _try_acquire_file_lock` | cross_community | 6 |
| `Connect → Get_hermes_home` | cross_community | 6 |
| `Connect → _get_process_start_time` | cross_community | 6 |
| `Join_voice_channel → _custom_unit_to_cp` | cross_community | 6 |
| `Connect → _utc_now_iso` | cross_community | 5 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Platforms | 72 calls |
| Hermes_cli | 22 calls |
| Tools | 16 calls |
| Tests | 4 calls |
| Qqbot | 3 calls |
| Run_agent | 2 calls |
| Cluster_1 | 2 calls |
| Tui_gateway | 2 calls |

## How to Explore

1. `gitnexus_context({name: "test_search_sessions_exposes_last_active_column"})` — see callers and callees
2. `gitnexus_query({query: "gateway"})` — find related execution flows
3. Read key files listed above for implementation details
