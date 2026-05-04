---
name: environments
description: "Skill for the Environments area of hermes-agent. 146 symbols across 24 files."
---

# Environments

146 symbols | 24 files | Cohesion: 72%

## When to Use

- Working with code in `tools/`
- Understanding how exec_fn, get_sandbox_dir, get_skills_directory_mount work
- Modifying environments-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tools/environments/vercel_sandbox.py` | _snapshot_store_path, _load_snapshots, _save_snapshots, _get_snapshot_id, _store_snapshot (+21) |
| `tools/environments/base.py` | _load_json_store, _run_bash, _wrap_command, _embed_stdin_heredoc, _update_cwd (+17) |
| `tools/environments/managed_modal.py` | _start_modal_exec, _poll_modal_exec, _create_sandbox, _request, _cancel_exec (+5) |
| `tools/environments/singularity.py` | _get_scratch_dir, _get_apptainer_cache_dir, _get_or_build_sif, _find_singularity_executable, _ensure_singularity_available (+5) |
| `tools/environments/modal.py` | _load_snapshots, _save_snapshots, _direct_snapshot_key, _get_snapshot_restore_candidate, _store_direct_snapshot (+4) |
| `tools/environments/ssh.py` | __init__, _build_ssh_command, _establish_connection, _detect_remote_home, _ensure_remote_dirs (+3) |
| `environments/tool_context.py` | terminal, write_file, upload_file, upload_dir, download_file (+2) |
| `tools/environments/modal_utils.py` | _result, _error_result, execute, _prepare_modal_exec, _timeout_result_for_modal (+2) |
| `environments/hermes_base_env.py` | _resolve_tools_for_group, _use_managed_server, collect_trajectories, collect_trajectory, HermesAgentEnvConfig (+2) |
| `environments/agentic_opd_env.py` | compute_reward, collect_trajectories, evaluate, _apply_opd_pipeline, _opd_for_sequence (+1) |

## Entry Points

Start here when exploring this area:

- **`exec_fn`** (Function) — `tools/environments/vercel_sandbox.py:604`
- **`get_sandbox_dir`** (Function) — `tools/environments/base.py:80`
- **`get_skills_directory_mount`** (Function) — `tools/credential_files.py:201`
- **`quoted_mkdir_command`** (Function) — `tools/environments/file_sync.py:82`
- **`unique_parent_dirs`** (Function) — `tools/environments/file_sync.py:87`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `BaseModalExecutionEnvironment` | Class | `tools/environments/modal_utils.py` | 57 |
| `ManagedModalEnvironment` | Class | `tools/environments/managed_modal.py` | 35 |
| `BaseEnvironment` | Class | `tools/environments/base.py` | 266 |
| `HermesAgentEnvConfig` | Class | `environments/hermes_base_env.py` | 77 |
| `TerminalBench2EvalConfig` | Class | `environments/benchmarks/terminalbench_2/terminalbench2_env.py` | 75 |
| `HermesAgentBaseEnv` | Class | `environments/hermes_base_env.py` | 220 |
| `TerminalBench2EvalEnv` | Class | `environments/benchmarks/terminalbench_2/terminalbench2_env.py` | 220 |
| `exec_fn` | Function | `tools/environments/vercel_sandbox.py` | 604 |
| `get_sandbox_dir` | Function | `tools/environments/base.py` | 80 |
| `get_skills_directory_mount` | Function | `tools/credential_files.py` | 201 |
| `quoted_mkdir_command` | Function | `tools/environments/file_sync.py` | 82 |
| `unique_parent_dirs` | Function | `tools/environments/file_sync.py` | 87 |
| `touch_activity_if_due` | Function | `tools/environments/base.py` | 54 |
| `find_docker` | Function | `tools/environments/docker.py` | 100 |
| `quoted_rm_command` | Function | `tools/environments/file_sync.py` | 77 |
| `resize_tool_pool` | Function | `environments/agent_loop.py` | 35 |
| `terminal` | Method | `environments/tool_context.py` | 81 |
| `write_file` | Method | `environments/tool_context.py` | 129 |
| `upload_file` | Method | `environments/tool_context.py` | 151 |
| `upload_dir` | Method | `environments/tool_context.py` | 205 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `Rollout_and_score_eval → _snapshot_state` | cross_community | 8 |
| `Execute → Get_session_env` | cross_community | 7 |
| `Execute → _get_sudo_password_callback` | cross_community | 7 |
| `Collect_trajectory → _snapshot_state` | cross_community | 7 |
| `Collect_trajectory → Get_registered_toolset_aliases` | cross_community | 7 |
| `Collect_trajectory → Get_toolset_alias_target` | cross_community | 7 |
| `Rollout_and_score_eval → Get_registered_toolset_aliases` | cross_community | 7 |
| `Rollout_and_score_eval → Get_toolset_alias_target` | cross_community | 7 |
| `Execute → _read_shell_token` | cross_community | 6 |
| `Execute → _looks_like_env_assignment` | cross_community | 6 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Tools | 22 calls |
| Run_agent | 5 calls |
| Hermes_cli | 4 calls |
| Tests | 2 calls |
| Agent | 1 calls |
| Terminalbench_2 | 1 calls |

## How to Explore

1. `gitnexus_context({name: "exec_fn"})` — see callers and callees
2. `gitnexus_query({query: "environments"})` — find related execution flows
3. Read key files listed above for implementation details
