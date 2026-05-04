---
name: integration
description: "Skill for the Integration area of hermes-agent. 67 symbols across 7 files."
---

# Integration

67 symbols | 7 files | Cohesion: 90%

## When to Use

- Working with code in `tests/`
- Understanding how print_section, print_error, create_test_dataset work
- Modifying integration-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/integration/test_voice_channel_flow.py` | _make_secret_key, _build_encrypted_rtp_packet, _build_padded_rtp_packet, _make_voice_receiver, test_valid_encrypted_packet_buffered (+33) |
| `tests/integration/test_web_tools.py` | print_section, print_error, log_result, test_environment, test_web_search (+8) |
| `tests/integration/test_ha_integration.py` | _adapter_for, test_connect_auth_subscribe, test_connect_auth_rejected, test_event_received_and_forwarded, test_event_filtering_ignores_unwatched (+1) |
| `tests/integration/test_checkpoint_resumption.py` | create_test_dataset, _cleanup_test_artifacts, test_current_implementation, test_interruption_and_resume, main |
| `gateway/platforms/homeassistant.py` | connect, disconnect |
| `batch_runner.py` | _save_checkpoint, run |
| `tools/web_tools.py` | check_auxiliary_model |

## Entry Points

Start here when exploring this area:

- **`print_section`** (Function) — `tests/integration/test_web_tools.py:60`
- **`print_error`** (Function) — `tests/integration/test_web_tools.py:71`
- **`create_test_dataset`** (Function) — `tests/integration/test_checkpoint_resumption.py:36`
- **`test_current_implementation`** (Function) — `tests/integration/test_checkpoint_resumption.py:120`
- **`test_interruption_and_resume`** (Function) — `tests/integration/test_checkpoint_resumption.py:215`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `print_section` | Function | `tests/integration/test_web_tools.py` | 60 |
| `print_error` | Function | `tests/integration/test_web_tools.py` | 71 |
| `create_test_dataset` | Function | `tests/integration/test_checkpoint_resumption.py` | 36 |
| `test_current_implementation` | Function | `tests/integration/test_checkpoint_resumption.py` | 120 |
| `test_interruption_and_resume` | Function | `tests/integration/test_checkpoint_resumption.py` | 215 |
| `main` | Function | `tests/integration/test_checkpoint_resumption.py` | 389 |
| `check_auxiliary_model` | Function | `tools/web_tools.py` | 1974 |
| `print_warning` | Function | `tests/integration/test_web_tools.py` | 76 |
| `print_info` | Function | `tests/integration/test_web_tools.py` | 81 |
| `main` | Function | `tests/integration/test_web_tools.py` | 591 |
| `test_valid_encrypted_packet_buffered` | Method | `tests/integration/test_voice_channel_flow.py` | 145 |
| `test_wrong_key_packet_dropped` | Method | `tests/integration/test_voice_channel_flow.py` | 157 |
| `test_bot_ssrc_ignored` | Method | `tests/integration/test_voice_channel_flow.py` | 169 |
| `test_multiple_packets_accumulate` | Method | `tests/integration/test_voice_channel_flow.py` | 179 |
| `test_different_ssrcs_separate_buffers` | Method | `tests/integration/test_voice_channel_flow.py` | 194 |
| `test_dave_unknown_ssrc_passthrough` | Method | `tests/integration/test_voice_channel_flow.py` | 211 |
| `test_dave_unencrypted_error_passthrough` | Method | `tests/integration/test_voice_channel_flow.py` | 226 |
| `test_dave_real_error_drops` | Method | `tests/integration/test_voice_channel_flow.py` | 244 |
| `test_padded_packet_stripped_and_buffered` | Method | `tests/integration/test_voice_channel_flow.py` | 261 |
| `test_padded_packet_matches_unpadded_output` | Method | `tests/integration/test_voice_channel_flow.py` | 274 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Tools | 10 calls |
| Platforms | 4 calls |
| Cluster_1 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "print_section"})` — see callers and callees
2. `gitnexus_query({query: "integration"})` — find related execution flows
3. Read key files listed above for implementation details
