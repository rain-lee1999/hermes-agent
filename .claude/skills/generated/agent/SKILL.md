---
name: agent
description: "Skill for the Agent area of hermes-agent. 989 symbols across 111 files."
---

# Agent

989 symbols | 111 files | Cohesion: 69%

## When to Use

- Working with code in `agent/`
- Understanding how get_codex_auth_status, load_pool, test_fill_first_selection_skips_recently_exhausted_entry work
- Modifying agent-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `agent/auxiliary_client.py` | _extract_codex_quota_percents, _get_codex_low_quota_thresholds, _codex_entry_below_low_quota, _is_payment_error, _is_connection_error (+71) |
| `tests/agent/test_memory_provider.py` | test_get_provider_by_name, test_builtin_plus_external, test_second_external_rejected, test_on_turn_start, test_on_pre_compress (+42) |
| `tests/agent/test_credential_pool.py` | _write_auth_store, test_fill_first_selection_skips_recently_exhausted_entry, test_select_clears_expired_exhaustion, test_round_robin_strategy_rotates_priorities, test_random_strategy_uses_random_choice (+35) |
| `agent/anthropic_adapter.py` | _is_oauth_token, _read_claude_code_credentials_from_keychain, read_claude_code_credentials, is_claude_code_token_valid, _resolve_claude_code_token_from_credentials (+29) |
| `agent/credential_pool.py` | select, acquire_lease, load_pool, has_available, _replace_entry (+28) |
| `tests/agent/test_skill_commands.py` | _make_skill, test_finds_skills, test_excludes_incompatible_platform, test_includes_matching_platform, test_universal_skill_on_any_platform (+27) |
| `agent/model_metadata.py` | _strip_provider_prefix, _infer_provider_from_url, _is_known_provider_base_url, _get_context_cache_path, _load_context_cache (+24) |
| `agent/google_oauth.py` | _credentials_path, _lock_path, _credentials_lock, parse, from_dict (+22) |
| `tests/agent/test_auxiliary_named_custom_providers.py` | _write_config, test_main_resolves_to_named_custom_provider, test_main_with_custom_colon_prefix, test_main_resolves_github_copilot_alias, test_named_custom_provider (+20) |
| `agent/display.py` | _diff_ansi, _hex_fg, _diff_dim, _diff_file, _diff_hunk (+19) |

## Entry Points

Start here when exploring this area:

- **`get_codex_auth_status`** (Function) — `hermes_cli/auth.py:3365`
- **`load_pool`** (Function) — `agent/credential_pool.py:1598`
- **`test_fill_first_selection_skips_recently_exhausted_entry`** (Function) — `tests/agent/test_credential_pool.py:16`
- **`test_select_clears_expired_exhaustion`** (Function) — `tests/agent/test_credential_pool.py:61`
- **`test_round_robin_strategy_rotates_priorities`** (Function) — `tests/agent/test_credential_pool.py:94`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `MemoryProvider` | Class | `agent/memory_provider.py` | 42 |
| `FakeMemoryProvider` | Class | `tests/agent/test_memory_provider.py` | 14 |
| `ImageGenProvider` | Class | `agent/image_gen_provider.py` | 50 |
| `OpenAIImageGenProvider` | Class | `plugins/image_gen/openai/__init__.py` | 123 |
| `ContextEngine` | Class | `agent/context_engine.py` | 31 |
| `get_codex_auth_status` | Function | `hermes_cli/auth.py` | 3365 |
| `load_pool` | Function | `agent/credential_pool.py` | 1598 |
| `test_fill_first_selection_skips_recently_exhausted_entry` | Function | `tests/agent/test_credential_pool.py` | 16 |
| `test_select_clears_expired_exhaustion` | Function | `tests/agent/test_credential_pool.py` | 61 |
| `test_round_robin_strategy_rotates_priorities` | Function | `tests/agent/test_credential_pool.py` | 94 |
| `test_random_strategy_uses_random_choice` | Function | `tests/agent/test_credential_pool.py` | 138 |
| `test_exhausted_entry_resets_after_ttl` | Function | `tests/agent/test_credential_pool.py` | 181 |
| `test_exhausted_402_entry_resets_after_one_hour` | Function | `tests/agent/test_credential_pool.py` | 216 |
| `test_explicit_reset_timestamp_overrides_default_429_ttl` | Function | `tests/agent/test_credential_pool.py` | 252 |
| `test_mark_exhausted_and_rotate_persists_status` | Function | `tests/agent/test_credential_pool.py` | 290 |
| `test_load_pool_seeds_env_api_key` | Function | `tests/agent/test_credential_pool.py` | 335 |
| `test_load_pool_removes_stale_seeded_env_entry` | Function | `tests/agent/test_credential_pool.py` | 350 |
| `test_load_pool_migrates_nous_provider_state` | Function | `tests/agent/test_credential_pool.py` | 383 |
| `test_load_pool_removes_stale_file_backed_singleton_entry` | Function | `tests/agent/test_credential_pool.py` | 418 |
| `test_load_pool_migrates_nous_provider_state_preserves_tls` | Function | `tests/agent/test_credential_pool.py` | 463 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Main → _to_openai_base_url` | cross_community | 10 |
| `Main → _fixed_temperature_for_model` | cross_community | 10 |
| `Main → _coerce_summary_content` | cross_community | 9 |
| `Main → _ensure_summary_prefix` | cross_community | 9 |
| `Generate → _replace_entry` | cross_community | 7 |
| `Generate → Current` | cross_community | 7 |
| `Generate → _is_suppressed` | cross_community | 7 |
| `Generate → From_dict` | cross_community | 6 |
| `Generate → _auth_file_path` | cross_community | 6 |
| `Generate → Get_hermes_home` | cross_community | 6 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Hermes_cli | 116 calls |
| Tools | 24 calls |
| Tests | 8 calls |
| Gateway | 5 calls |
| Cluster_1 | 3 calls |
| Memory | 2 calls |
| Xai | 2 calls |
| Run_agent | 1 calls |

## How to Explore

1. `gitnexus_context({name: "get_codex_auth_status"})` — see callers and callees
2. `gitnexus_query({query: "agent"})` — find related execution flows
3. Read key files listed above for implementation details
