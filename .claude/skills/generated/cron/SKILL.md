---
name: cron
description: "Skill for the Cron area of hermes-agent. 157 symbols across 19 files."
---

# Cron

157 symbols | 19 files | Cohesion: 82%

## When to Use

- Working with code in `tests/`
- Understanding how now, cronjob, parse_duration work
- Modifying cron-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `tests/cron/test_jobs.py` | test_create_and_get, test_remove_job, test_update_name, test_update_schedule, test_update_enable_disable (+26) |
| `cron/jobs.py` | _normalize_skill_list, _apply_skill_fields, parse_duration, parse_schedule, _ensure_aware (+21) |
| `tests/cron/test_scheduler.py` | _make_job, test_wake_false_skips_agent_and_returns_silent, test_wake_true_runs_agent_with_injected_output, test_script_runs_only_once_on_wake, test_script_failure_does_not_trigger_gate (+13) |
| `tests/cron/test_cron_context_from.py` | test_create_job_with_context_from_string, test_update_adds_context_from_to_existing_job, test_update_changes_context_from_reference, test_update_clears_context_from_with_empty_list, test_update_clears_context_from_with_empty_string (+11) |
| `tests/cron/test_rewrite_skill_refs.py` | test_jobs_exist_but_map_empty, test_jobs_exist_but_no_match, test_single_skill_replaced, test_multiple_skills_one_consolidated, test_umbrella_already_in_list_dedupes (+10) |
| `cron/scheduler.py` | _resolve_cron_enabled_toolsets, _parse_wake_gate, run_job, _get_script_timeout, _run_job_script (+9) |
| `tests/cron/test_cron_workdir.py` | test_workdir_stored_when_set, test_workdir_none_preserves_old_behaviour, test_set_workdir_via_update, test_clear_workdir_with_none, test_clear_workdir_with_empty_string (+4) |
| `tests/test_timezone.py` | _reset_hermes_time_cache, test_cache_invalidation, test_get_due_jobs_handles_naive_timestamps, test_ensure_aware_naive_preserves_absolute_time, test_ensure_aware_normalizes_aware_to_hermes_tz (+3) |
| `tests/tools/test_cronjob_tools.py` | test_create_normalizes_list_form_deliver, test_create_normalizes_multi_element_list_deliver, test_update_normalizes_list_form_deliver |
| `tests/cron/test_cron_script.py` | test_create_job_with_script, test_update_job_add_script, test_update_job_clear_script |

## Entry Points

Start here when exploring this area:

- **`now`** (Function) — `hermes_time.py:90`
- **`cronjob`** (Function) — `tools/cronjob_tools.py:245`
- **`parse_duration`** (Function) — `cron/jobs.py:102`
- **`parse_schedule`** (Function) — `cron/jobs.py:123`
- **`compute_next_run`** (Function) — `cron/jobs.py:290`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `now` | Function | `hermes_time.py` | 90 |
| `cronjob` | Function | `tools/cronjob_tools.py` | 245 |
| `parse_duration` | Function | `cron/jobs.py` | 102 |
| `parse_schedule` | Function | `cron/jobs.py` | 123 |
| `compute_next_run` | Function | `cron/jobs.py` | 290 |
| `load_jobs` | Function | `cron/jobs.py` | 340 |
| `save_jobs` | Function | `cron/jobs.py` | 369 |
| `create_job` | Function | `cron/jobs.py` | 421 |
| `get_job` | Function | `cron/jobs.py` | 552 |
| `update_job` | Function | `cron/jobs.py` | 569 |
| `pause_job` | Function | `cron/jobs.py` | 617 |
| `resume_job` | Function | `cron/jobs.py` | 630 |
| `trigger_job` | Function | `cron/jobs.py` | 649 |
| `remove_job` | Function | `cron/jobs.py` | 666 |
| `mark_job_run` | Function | `cron/jobs.py` | 677 |
| `advance_next_run` | Function | `cron/jobs.py` | 750 |
| `get_due_jobs` | Function | `cron/jobs.py` | 779 |
| `rewrite_skill_refs` | Function | `cron/jobs.py` | 890 |
| `apply_ipv4_preference` | Function | `hermes_constants.py` | 249 |
| `format_runtime_provider_error` | Function | `hermes_cli/runtime_provider.py` | 1336 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Hermes_cli | 11 calls |
| Tools | 10 calls |
| Gateway | 6 calls |
| Agent | 5 calls |
| Tests | 2 calls |
| Tui_gateway | 1 calls |

## How to Explore

1. `gitnexus_context({name: "now"})` — see callers and callees
2. `gitnexus_query({query: "cron"})` — find related execution flows
3. Read key files listed above for implementation details
