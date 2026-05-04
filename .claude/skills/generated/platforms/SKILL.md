---
name: platforms
description: "Skill for the Platforms area of hermes-agent. 925 symbols across 52 files."
---

# Platforms

925 symbols | 52 files | Cohesion: 65%

## When to Use

- Working with code in `gateway/`
- Understanding how is_safe_url, resolve_proxy_url, proxy_kwargs_for_aiohttp work
- Modifying platforms-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `gateway/platforms/feishu.py` | send_animation, _download_remote_document, _download_feishu_message_resources, _download_feishu_image, _download_feishu_message_resource (+127) |
| `gateway/platforms/yuanbao.py` | _extract_connect_id, next_fn, handle, handle, _extract_text (+80) |
| `gateway/platforms/telegram.py` | _metadata_thread_id, _message_thread_id_for_send, _is_thread_not_found_error, _link_preview_kwargs, send (+54) |
| `gateway/platforms/weixin.py` | _aes128_ecb_encrypt, _deliver_media, send_document, send_video, send_voice (+52) |
| `gateway/platforms/discord.py` | send, _forum_post_file, _send_file_attachment, send_multiple_images, send_voice (+50) |
| `gateway/platforms/base.py` | resolve_proxy_url, proxy_kwargs_for_aiohttp, send_multiple_images, send_image, send_animation (+50) |
| `gateway/platforms/wecom.py` | _wait_for_handshake, _read_events, _dispatch_payload, _payload_req_id, _parse_json (+48) |
| `gateway/platforms/matrix.py` | send_image, _handle_media_message, _mxc_to_http, __init__, send_image_file (+40) |
| `gateway/platforms/api_server.py` | _openai_error, _check_auth, _handle_get_response, _handle_delete_response, _set_run_status (+40) |
| `gateway/platforms/slack.py` | _download_slack_file, _get_client, send, _resolve_thread_ts, _upload_file (+38) |

## Entry Points

Start here when exploring this area:

- **`is_safe_url`** (Function) — `tools/url_safety.py:154`
- **`resolve_proxy_url`** (Function) — `gateway/platforms/base.py:280`
- **`proxy_kwargs_for_aiohttp`** (Function) — `gateway/platforms/base.py:344`
- **`decode_inbound_push`** (Function) — `gateway/platforms/yuanbao_proto.py:636`
- **`decode_query_group_info_rsp`** (Function) — `gateway/platforms/yuanbao_proto.py:1075`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `is_safe_url` | Function | `tools/url_safety.py` | 154 |
| `resolve_proxy_url` | Function | `gateway/platforms/base.py` | 280 |
| `proxy_kwargs_for_aiohttp` | Function | `gateway/platforms/base.py` | 344 |
| `decode_inbound_push` | Function | `gateway/platforms/yuanbao_proto.py` | 636 |
| `decode_query_group_info_rsp` | Function | `gateway/platforms/yuanbao_proto.py` | 1075 |
| `decode_get_group_member_list_rsp` | Function | `gateway/platforms/yuanbao_proto.py` | 1156 |
| `encode_conn_msg_full` | Function | `gateway/platforms/yuanbao_proto.py` | 388 |
| `encode_auth_bind` | Function | `gateway/platforms/yuanbao_proto.py` | 911 |
| `get_image_cache_dir` | Function | `gateway/platforms/base.py` | 502 |
| `cache_image_from_bytes` | Function | `gateway/platforms/base.py` | 525 |
| `cache_audio_from_bytes` | Function | `gateway/platforms/base.py` | 649 |
| `next_fn` | Function | `gateway/platforms/yuanbao.py` | 1043 |
| `cache_video_from_bytes` | Function | `gateway/platforms/base.py` | 750 |
| `next_seq_no` | Function | `gateway/platforms/yuanbao_proto.py` | 112 |
| `encode_biz_msg` | Function | `gateway/platforms/yuanbao_proto.py` | 428 |
| `encode_send_private_heartbeat` | Function | `gateway/platforms/yuanbao_proto.py` | 993 |
| `encode_send_group_heartbeat` | Function | `gateway/platforms/yuanbao_proto.py` | 1020 |
| `encode_query_group_info` | Function | `gateway/platforms/yuanbao_proto.py` | 1058 |
| `encode_get_group_member_list` | Function | `gateway/platforms/yuanbao_proto.py` | 1130 |
| `has_wiki_keys` | Function | `gateway/platforms/feishu_comment_rules.py` | 164 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Collect_trajectory → Is_registered` | cross_community | 6 |
| `Connect → _normalize_whatsapp_id` | cross_community | 6 |
| `Connect → _allows_private_ip_resolution` | cross_community | 6 |
| `Connect → _is_blocked_ip` | cross_community | 6 |
| `Connect → _looks_like_image` | cross_community | 6 |
| `Join_voice_channel → Format_message` | cross_community | 6 |
| `Join_voice_channel → _derive_forum_thread_name` | cross_community | 6 |
| `Join_voice_channel → _custom_unit_to_cp` | cross_community | 6 |
| `Rollout_and_score_eval → Is_registered` | cross_community | 6 |
| `Connect → _utc_now_iso` | cross_community | 5 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Gateway | 101 calls |
| Tests | 26 calls |
| Qqbot | 21 calls |
| Hermes_cli | 19 calls |
| Tools | 16 calls |
| Cluster_1 | 6 calls |
| Agent | 3 calls |
| Cron | 1 calls |

## How to Explore

1. `gitnexus_context({name: "is_safe_url"})` — see callers and callees
2. `gitnexus_query({query: "platforms"})` — find related execution flows
3. Read key files listed above for implementation details
