---
name: scripts
description: "Skill for the Scripts area of hermes-agent. 488 symbols across 52 files."
---

# Scripts

488 symbols | 52 files | Cohesion: 81%

## When to Use

- Working with code in `optional-skills/`
- Understanding how sha256_file, read_text, ensure_parent work
- Modifying scripts-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py` | sha256_file, read_text, ensure_parent, resolve_secret_input, load_yaml_file (+71) |
| `optional-skills/productivity/telephony/scripts/telephony.py` | _twilio_creds, _twilio_basic_headers, _twilio_request, _twilio_owned_numbers, _twilio_search_numbers (+39) |
| `skills/creative/comfyui/scripts/_common.py` | json, http_request, http_post, safe_path_join, media_type_from_filename (+20) |
| `optional-skills/blockchain/base/scripts/base_client.py` | _http_get_json, _rpc_call, rpc_batch, wei_to_eth, wei_to_gwei (+17) |
| `scripts/reorder_codex_by_menubar_quota.py` | quota_percent, effective_remaining_percent, row_id_from_entry, resolve_entry_row, reorder_entries (+17) |
| `skills/productivity/google-workspace/scripts/google_api.py` | _ensure_authenticated, _gws_binary, _run_gws, _headers_dict, get_credentials (+16) |
| `skills/productivity/maps/scripts/maps_client.py` | _tags_for, print_json, error_exit, http_get, http_post (+15) |
| `optional-skills/productivity/memento-flashcards/scripts/memento_cards.py` | _now, _iso, _parse_iso, _load, _save (+12) |
| `optional-skills/creative/meme-generation/scripts/generate_meme.py` | _default_fields, find_font, _wrap_text, draw_outlined_text, _overlay_on_image (+12) |
| `skills/creative/comfyui/scripts/run_workflow.py` | _url, check_server, upload_image, submit, poll_status (+11) |

## Entry Points

Start here when exploring this area:

- **`sha256_file`** (Function) — `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py:305`
- **`read_text`** (Function) — `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py:313`
- **`ensure_parent`** (Function) — `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py:321`
- **`resolve_secret_input`** (Function) — `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py:325`
- **`load_yaml_file`** (Function) — `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py:348`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `sha256_file` | Function | `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py` | 305 |
| `read_text` | Function | `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py` | 313 |
| `ensure_parent` | Function | `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py` | 321 |
| `resolve_secret_input` | Function | `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py` | 325 |
| `load_yaml_file` | Function | `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py` | 348 |
| `dump_yaml_file` | Function | `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py` | 355 |
| `parse_env_file` | Function | `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py` | 365 |
| `save_env_file` | Function | `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py` | 378 |
| `backup_existing` | Function | `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py` | 384 |
| `rpc_batch` | Function | `optional-skills/blockchain/base/scripts/base_client.py` | 165 |
| `wei_to_eth` | Function | `optional-skills/blockchain/base/scripts/base_client.py` | 183 |
| `wei_to_gwei` | Function | `optional-skills/blockchain/base/scripts/base_client.py` | 187 |
| `hex_to_int` | Function | `optional-skills/blockchain/base/scripts/base_client.py` | 191 |
| `print_json` | Function | `optional-skills/blockchain/base/scripts/base_client.py` | 198 |
| `fetch_prices` | Function | `optional-skills/blockchain/base/scripts/base_client.py` | 267 |
| `fetch_eth_price` | Function | `optional-skills/blockchain/base/scripts/base_client.py` | 292 |
| `resolve_token_name` | Function | `optional-skills/blockchain/base/scripts/base_client.py` | 302 |
| `cmd_stats` | Function | `optional-skills/blockchain/base/scripts/base_client.py` | 333 |
| `cmd_wallet` | Function | `optional-skills/blockchain/base/scripts/base_client.py` | 381 |
| `cmd_tx` | Function | `optional-skills/blockchain/base/scripts/base_client.py` | 497 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → _to_openai_base_url` | cross_community | 10 |
| `Main → _fixed_temperature_for_model` | cross_community | 10 |
| `Main → Count_tokens` | cross_community | 9 |
| `Main → _coerce_summary_content` | cross_community | 9 |
| `Main → _ensure_summary_prefix` | cross_community | 9 |
| `Main → _find_protected_indices` | cross_community | 8 |
| `Main → _extract_turn_content_for_summary` | cross_community | 8 |
| `Migrate → _normalize_secret_key` | cross_community | 7 |
| `Main → _find_protected_indices` | cross_community | 7 |
| `Main → _extract_turn_content_for_summary` | cross_community | 7 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Tools | 2 calls |
| Cluster_8 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "sha256_file"})` — see callers and callees
2. `gitnexus_query({query: "scripts"})` — find related execution flows
3. Read key files listed above for implementation details
