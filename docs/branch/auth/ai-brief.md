---
branch: auth
purpose: Codex account stickiness, Menubar auth sync, and conservative five-hour quota priming
read_first: README.md
spec: null
plan: null
primary_files:
  - cli.py
  - run_agent.py
  - hermes_cli/runtime_provider.py
  - agent/auxiliary_client.py
  - agent/credential_pool.py
  - scripts/reorder_codex_by_menubar_quota.py
  - scripts/HermesCodexAccountSyncWatcher
  - tests/scripts/test_reorder_codex_by_menubar_quota.py
  - tests/scripts/test_codex_menubar_sync_watcher.py
---

# auth AI brief

## One-line summary

This branch makes Hermes Codex account behavior truthful and sticky: same-session turns reuse the selected credential, Menubar-ranked account order syncs into Hermes auth state, and 100% five-hour quota accounts can be conservatively primed once to start their refresh window.

## Must-know concepts

- Session-bound runtime credential: a Hermes session should keep its chosen credential until a real failover or session boundary.
- Menubar-first ordering: `last-menu-rows.json` is already ranked; Hermes preserves that order instead of re-sorting.
- Pool vs singleton: `credential_pool.openai-codex` and `providers.openai-codex.tokens` must converge or direct readers can use the wrong account.
- Five-hour prime: if an account is 100% and its reset still looks like a full 5h window, send one minimal non-stored Codex response to start the window.
- Runtime vs repo: `~/.hermes` auth/prime state is installed runtime state, not branch-local source code.

## Before vs after

### Before

- Auxiliary paths could reload the Codex pool and reselect the top account inside an existing session.
- Menubar sync did not cover all truth surfaces equally: pool ordering, singleton tokens, labels/imported_from, and duplicated manual entries could diverge.
- The watcher only synced auth order; 100% five-hour accounts could remain stuck showing a future 5h refresh because nothing consumed them.

### After

- Main and auxiliary runtime paths preserve selected credential metadata where appropriate.
- `reorder_codex_by_menubar_quota.py` syncs Menubar-ranked rows into Hermes pool and provider singleton.
- `--prime-full-five-hour` detects full 5h/100% rows and posts a tiny Codex Responses request with `store=false`.
- Prime state records both `row_id + fiveHourResetAt` and a 5-hour per-account cooldown to prevent short-interval repeated triggers.
- `HermesCodexAccountSyncWatcher` now runs sync with `--prime-full-five-hour` and logs prime counts.

## Invariants to preserve

1. Same-session append must not reselect the top-ranked account unless there is real credential failure/failover.
2. New sessions, `/new`, and first delegate creation may choose the current highest-priority available account.
3. Menubar row order must remain the source of truth for Hermes Codex pool priority.
4. Pool entry labels/imported_from/account_id must match the actual token material they represent.
5. Five-hour prime must stay minimal, non-stored, independent from current Hermes conversation history, and rate-limited per account.
6. Failed prime attempts must be reported but should not block normal auth sync or permanently mark the account primed.

## Where to look in code

- `scripts/reorder_codex_by_menubar_quota.py`
  - `build_ranking`, `sync_entries`, `reorder_entries`, `sync_provider_singleton_from_primary_entry`
  - five-hour prime helpers: `five_hour_prime_candidates`, `prime_five_hour_row`, `prime_full_five_hour_rows`, `row_recently_primed`
- `scripts/HermesCodexAccountSyncWatcher`
  - `run_sync()` now passes `--prime-full-five-hour` and summarizes prime counts.
- `agent/credential_pool.py`
  - pool entry truth, refresh, singleton sync, failover status.
- `agent/auxiliary_client.py`
  - auxiliary runtime routing and Codex explicit credential handling.
- `run_agent.py` / `cli.py`
  - selected credential propagation and session-boundary invalidation.
- `tests/scripts/test_reorder_codex_by_menubar_quota.py`
  - prime candidate, payload/header, cooldown regressions.
- `tests/scripts/test_codex_menubar_sync_watcher.py`
  - watcher command and summary regression.

## Fast mental model

Think of Codex account handling as three layers that must agree: Menubar decides account order, Hermes auth state mirrors that truth, and live Hermes sessions keep their selected credential stable. The new prime path is outside the conversation path: it is a tiny maintenance request used only to start a five-hour refresh timer.

## Verification

Recent scoped verification:

- `gitnexus analyze`: pass.
- GitNexus impact on sync script symbols: LOW before editing.
- RED/GREEN for five-hour prime and per-account cooldown: observed.
- `scripts/run_tests.sh tests/scripts/test_reorder_codex_by_menubar_quota.py tests/scripts/test_codex_menubar_sync_watcher.py -q`: 9 passed.
- `python3 scripts/reorder_codex_by_menubar_quota.py --quiet`: dry-run OK; no apply means no prime.
- `git diff --check`: pass.
- GitNexus detect-changes: medium, limited to expected sync-script flows.

Testing note: this worktree lacks its own venv, so validation temporarily symlinked `venv` to `/Users/rain/hermes-agent/venv`; the symlink was removed after tests.

## Future work usually looks like

- Add regressions whenever a new Codex reader could bypass pool/selected credential truth.
- If Menubar changes its row schema or ranking semantics, update sync logic and docs together.
- If Codex changes Responses endpoint/model allow-list, adjust `resolve_prime_model` / prime request shape with tests.
- Keep prime conservative: no large prompts, no transcript/session writes, no short-loop retries.
