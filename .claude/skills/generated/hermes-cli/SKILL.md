---
name: hermes-cli
description: "Skill for the Hermes_cli area of hermes-agent. 1994 symbols across 195 files."
---

# Hermes_cli

1994 symbols | 195 files | Cohesion: 65%

## When to Use

- Working with code in `hermes_cli/`
- Understanding how display_hermes_home, managed_nous_tools_enabled, resolve_openai_audio_api_key work
- Modifying hermes_cli-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `hermes_cli/gateway.py` | _setup_standard_platform, _setup_dingtalk, _setup_wecom, _setup_weixin, _setup_feishu (+97) |
| `hermes_cli/main.py` | cmd_whatsapp, select_provider_and_model, _named_custom_provider_map, _clear_stale_openai_base_url, _format_aux_current (+85) |
| `hermes_cli/auth.py` | get_anthropic_key, format_auth_error, deactivate_provider, _get_config_hint_for_unknown_provider, resolve_provider (+85) |
| `hermes_cli/models.py` | is_nous_free_tier, partition_nous_models_by_tier, check_nous_free_tier, _format_price_per_mtok, get_pricing_for_provider (+55) |
| `hermes_cli/web_server.py` | get_status, _normalize_config_for_web, get_config, set_model_assignment, get_skills (+52) |
| `hermes_cli/config.py` | is_managed, managed_error, get_config_path, get_env_path, get_project_root (+45) |
| `hermes_cli/plugins_cmd.py` | _plugins_dir, _sanitize_plugin_name, _resolve_git_url, _repo_name_from_url, _read_manifest (+38) |
| `hermes_cli/kanban_db.py` | workspaces_root, write_txn, _claimer_id, create_task, _find_missing_parents (+38) |
| `hermes_cli/setup.py` | _get_credential_pool_strategies, _set_credential_pool_strategy, print_header, print_noninteractive_setup_guidance, prompt (+36) |
| `hermes_cli/tools_config.py` | _toolset_allowed_for_platform, _get_effective_configurable_toolsets, _get_plugin_toolset_keys, _run_post_setup, _get_enabled_platforms (+30) |

## Entry Points

Start here when exploring this area:

- **`display_hermes_home`** (Function) — `hermes_constants.py:94`
- **`managed_nous_tools_enabled`** (Function) — `tools/tool_backend_helpers.py:16`
- **`resolve_openai_audio_api_key`** (Function) — `tools/tool_backend_helpers.py:102`
- **`prefers_gateway`** (Function) — `tools/tool_backend_helpers.py:110`
- **`resolve_managed_tool_gateway`** (Function) — `tools/managed_tool_gateway.py:131`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `ProfileGatewayProcess` | Class | `hermes_cli/gateway.py` | 64 |
| `ScanResult` | Class | `tools/skills_guard.py` | 71 |
| `GatewayRuntimeSnapshot` | Class | `hermes_cli/gateway.py` | 47 |
| `display_hermes_home` | Function | `hermes_constants.py` | 94 |
| `managed_nous_tools_enabled` | Function | `tools/tool_backend_helpers.py` | 16 |
| `resolve_openai_audio_api_key` | Function | `tools/tool_backend_helpers.py` | 102 |
| `prefers_gateway` | Function | `tools/tool_backend_helpers.py` | 110 |
| `resolve_managed_tool_gateway` | Function | `tools/managed_tool_gateway.py` | 131 |
| `is_managed_tool_gateway_ready` | Function | `tools/managed_tool_gateway.py` | 156 |
| `get_status` | Function | `hermes_cli/web_server.py` | 510 |
| `get_config` | Function | `hermes_cli/web_server.py` | 835 |
| `set_model_assignment` | Function | `hermes_cli/web_server.py` | 1052 |
| `get_skills` | Function | `hermes_cli/web_server.py` | 2606 |
| `toggle_skill` | Function | `hermes_cli/web_server.py` | 2618 |
| `get_toolsets` | Function | `hermes_cli/web_server.py` | 2631 |
| `get_dashboard_themes` | Function | `hermes_cli/web_server.py` | 3480 |
| `set_dashboard_theme` | Function | `hermes_cli/web_server.py` | 3515 |
| `get_dashboard_plugins` | Function | `hermes_cli/web_server.py` | 3619 |
| `put_plugin_providers` | Function | `hermes_cli/web_server.py` | 3860 |
| `post_plugin_visibility` | Function | `hermes_cli/web_server.py` | 3880 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Cmd_mcp_configure → Get_hermes_home` | cross_community | 10 |
| `Get_status → _is_container` | intra_community | 8 |
| `Get_status → Get_hermes_home` | cross_community | 8 |
| `Gateway_setup → _ensure_user_systemd_env` | cross_community | 8 |
| `Cmd_mcp_configure → _is_container` | intra_community | 8 |
| `Run_uninstall → Get_hermes_home` | cross_community | 8 |
| `Run_doctor → Get_default_hermes_root` | cross_community | 7 |
| `Setup_gateway → _parse_manifest` | cross_community | 7 |
| `Post_plugin_visibility → _is_container` | intra_community | 7 |
| `Run_uninstall → _try_acquire_file_lock` | cross_community | 7 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Agent | 121 calls |
| Tools | 106 calls |
| Gateway | 31 calls |
| Tests | 24 calls |
| Honcho | 7 calls |
| Memory | 7 calls |
| Cluster_1 | 6 calls |
| Cron | 6 calls |

## How to Explore

1. `gitnexus_context({name: "display_hermes_home"})` — see callers and callees
2. `gitnexus_query({query: "hermes_cli"})` — find related execution flows
3. Read key files listed above for implementation details
