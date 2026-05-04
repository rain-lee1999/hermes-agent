---
name: honcho
description: "Skill for the Honcho area of hermes-agent. 83 symbols across 7 files."
---

# Honcho

83 symbols | 7 files | Cohesion: 82%

## When to Use

- Working with code in `plugins/`
- Understanding how resolve_active_host, get_honcho_client, reset_honcho_client work
- Modifying honcho-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `plugins/memory/honcho/cli.py` | clone_honcho_for_profile, _ensure_peer_exists, cmd_enable, cmd_disable, cmd_sync (+25) |
| `plugins/memory/honcho/session.py` | seed_ai_identity, _get_or_create_peer, _sanitize_id, delete, dialectic_query (+22) |
| `plugins/memory/honcho/__init__.py` | _resolve_pass_level, _build_dialectic_prompt, _signal_sufficient, _run_dialectic_depth, _format_first_turn_context (+7) |
| `plugins/memory/honcho/client.py` | resolve_active_host, _resolve_optional_float, from_env, from_global_config, resolve_session_name (+4) |
| `tests/honcho_plugin/test_client.py` | test_truncation_is_deterministic, test_distinct_long_keys_do_not_collide, test_global_fallback_uses_home_at_call_time |
| `tests/honcho_plugin/test_session.py` | test_signal_sufficient_short_response |
| `tests/honcho_plugin/test_async_memory.py` | test_set_and_pop_context_result |

## Entry Points

Start here when exploring this area:

- **`resolve_active_host`** (Function) — `plugins/memory/honcho/client.py:33`
- **`get_honcho_client`** (Function) — `plugins/memory/honcho/client.py:667`
- **`reset_honcho_client`** (Function) — `plugins/memory/honcho/client.py:762`
- **`clone_honcho_for_profile`** (Function) — `plugins/memory/honcho/cli.py:17`
- **`cmd_enable`** (Function) — `plugins/memory/honcho/cli.py:94`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `resolve_active_host` | Function | `plugins/memory/honcho/client.py` | 33 |
| `get_honcho_client` | Function | `plugins/memory/honcho/client.py` | 667 |
| `reset_honcho_client` | Function | `plugins/memory/honcho/client.py` | 762 |
| `clone_honcho_for_profile` | Function | `plugins/memory/honcho/cli.py` | 17 |
| `cmd_enable` | Function | `plugins/memory/honcho/cli.py` | 94 |
| `cmd_disable` | Function | `plugins/memory/honcho/cli.py` | 137 |
| `cmd_sync` | Function | `plugins/memory/honcho/cli.py` | 154 |
| `sync_honcho_profiles_quiet` | Function | `plugins/memory/honcho/cli.py` | 200 |
| `cmd_setup` | Function | `plugins/memory/honcho/cli.py` | 356 |
| `cmd_status` | Function | `plugins/memory/honcho/cli.py` | 626 |
| `cmd_peers` | Function | `plugins/memory/honcho/cli.py` | 774 |
| `cmd_sessions` | Function | `plugins/memory/honcho/cli.py` | 791 |
| `cmd_map` | Function | `plugins/memory/honcho/cli.py` | 810 |
| `cmd_peer` | Function | `plugins/memory/honcho/cli.py` | 835 |
| `cmd_mode` | Function | `plugins/memory/honcho/cli.py` | 891 |
| `cmd_strategy` | Function | `plugins/memory/honcho/cli.py` | 925 |
| `cmd_tokens` | Function | `plugins/memory/honcho/cli.py` | 960 |
| `cmd_identity` | Function | `plugins/memory/honcho/cli.py` | 1004 |
| `cmd_migrate` | Function | `plugins/memory/honcho/cli.py` | 1078 |
| `honcho_command` | Function | `plugins/memory/honcho/cli.py` | 1307 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Run_doctor → Get_default_hermes_root` | cross_community | 7 |
| `Run_doctor → Get_hermes_home` | cross_community | 6 |
| `Honcho_command → _load_provider_from_dir` | cross_community | 5 |
| `Honcho_command → _is_memory_provider_dir` | cross_community | 5 |
| `Honcho_command → Get_hermes_home` | cross_community | 5 |
| `Honcho_command → _resolve_optional_float` | intra_community | 5 |
| `Honcho_command → _deep_merge` | cross_community | 4 |
| `Honcho_command → _normalize_root_model_keys` | cross_community | 4 |
| `Honcho_command → _enforce_session_id_limit` | intra_community | 4 |
| `Honcho_command → _git_repo_name` | intra_community | 4 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Hermes_cli | 14 calls |
| Honcho_plugin | 5 calls |

## How to Explore

1. `gitnexus_context({name: "resolve_active_host"})` — see callers and callees
2. `gitnexus_query({query: "honcho"})` — find related execution flows
3. Read key files listed above for implementation details
