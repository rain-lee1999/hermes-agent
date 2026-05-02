---
branch: update
purpose: make hermes update prefer a local source checkout and minimize default ~/.hermes mutations
read_first: README.md
spec: null
plan: null
primary_files:
  - hermes_cli/update_source.py
  - hermes_cli/main.py
  - hermes_cli/banner.py
  - hermes_cli/tips.py
  - tests/hermes_cli/test_update_source.py
  - tests/hermes_cli/test_update_check.py
  - tests/hermes_cli/test_cmd_update.py
  - tests/hermes_cli/test_update_yes_flag.py
---

# update AI brief

## One-line summary

`hermes update` now prefers a local source checkout such as `/Users/rain/dev/-github/hermes-agent/` over GitHub remotes, and update no longer defaults to bundled-skill sync or automatic config migration.

## Must-know concepts

- `resolve_local_update_source_repo(project_root)`: shared resolver for local update source checkout.
- Resolver order: `HERMES_UPDATE_SOURCE_REPO` → sibling with `-update` stripped → sibling `hermes-agent`.
- In this repo, `/Users/rain/dev/-github/hermes-agent-update` resolves to `/Users/rain/dev/-github/hermes-agent` when that checkout exists.
- Local-source update uses `git fetch --quiet <source> main`, compares `HEAD..FETCH_HEAD`, and pulls/resets against `<source> main` / `FETCH_HEAD`.
- Banner update checks and `hermes update --check` use the same local-source idea as the real update path.
- `~/.hermes` is treated as external persistent user state: default update should avoid automatic skills sync and config migration.

## Before vs after

### Before

- Update checks and update flow primarily targeted `origin/main` / fork/upstream remote logic.
- Bundled skills sync ran during update by default.
- Config drift/migration lived in the update path and could imply update owns `config.yaml` / `.env` changes.

### After

- Local source checkout is preferred when present; remote fallback remains when not present.
- Banner cache records `repo_dir` and `source_repo` so stale update-check results do not cross repo/source boundaries.
- Bundled skills sync runs only with `--sync-skills`; `--no-sync-skills` keeps it off.
- Config drift is reported only; user must run `hermes config migrate` separately.
- Zip pre-update backup is explicit/config-gated via `--backup` / `--no-backup`; quick snapshot protection still exists before actual pulls.

## Invariants to preserve

1. `cmd_update`, `hermes update --check`, and banner update check must not disagree about the preferred update source.
2. If a valid local source checkout exists, do not silently fetch/pull from `origin` first.
3. If no valid local source exists, remote/fork fallback must keep working.
4. Default `hermes update` must not automatically mutate bundled skills or config/env files.
5. `--yes` may suppress stash-restore prompts, but must not auto-fill API keys or auto-run config migration.
6. Any default touch of `~/.hermes` must be narrow and explainable: cache invalidation, logs, quick snapshot, or explicitly requested backup/sync.

## Where to look in code

- `hermes_cli/update_source.py`: local source resolution rules.
- `hermes_cli/main.py`:
  - `_cmd_update_check()` for `hermes update --check`.
  - `_cmd_update_impl()` for fetch/compare/pull/reset/source behavior.
  - `_run_pre_update_backup()` for zip backup flag/config behavior.
  - update argparse block near the bottom for `--backup`, `--no-backup`, `--sync-skills`, `--no-sync-skills`, `--yes`.
- `hermes_cli/banner.py`: startup update check, cache keys, local-source fetch.
- `hermes_cli/tips.py`: user-facing tip about explicit bundled-skill sync.
- `tests/hermes_cli/test_update_source.py`: resolver tests.
- `tests/hermes_cli/test_cmd_update.py`: local-source preference and skills-sync gating tests.
- `tests/hermes_cli/test_update_check.py`: banner/cache/check tests.
- `tests/hermes_cli/test_update_yes_flag.py`: config migration no longer happens in update.

## Fast mental model

Think of this branch as separating code update from user-state management. Code comes from the preferred local `main` checkout when available; user data changes require explicit commands or flags, except for narrow operational cache/snapshot safety behavior.

## Verification

- Repo inspected: `/Users/rain/dev/-github/hermes-agent-update`.
- Branch inspected: `update`.
- Base considered for broad comparison: `upstream/main` exists, but `upstream/main...HEAD` includes older carried work unrelated to this update task; this brief focuses on the current update-command dirty worktree.
- Previously reported targeted tests:
  - `scripts/run_tests.sh tests/hermes_cli/test_update_source.py tests/hermes_cli/test_update_check.py tests/hermes_cli/test_cmd_update.py tests/hermes_cli/test_update_autostash.py -q` → `40 passed`.
  - `scripts/run_tests.sh tests/hermes_cli/test_cmd_update.py tests/hermes_cli/test_update_yes_flag.py tests/hermes_cli/test_update_check.py tests/hermes_cli/test_update_source.py -q` → `22 passed`.
  - `scripts/run_tests.sh tests/hermes_cli/test_backup.py -q` → `93 passed`.
- This docs pass did not rerun the full suite.

## Future work usually looks like

- Add a new update-source override or resolver rule in `hermes_cli/update_source.py`, then update all three consumers and tests.
- Add/update tests before changing default `~/.hermes` side effects.
- Keep branch docs explicit about repo-local changes vs installed `hermes` runtime state.
