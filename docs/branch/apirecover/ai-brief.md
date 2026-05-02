---
branch: apirecover
purpose: API recovery strategy for Hermes Agent
read_first: README.md
spec: ../../specs/api-recovery-strategy.md
plan: ../../plans/api-recovery-strategy-plan.md
primary_files:
  - run_agent.py
  - cli.py
  - hermes_cli/plugins.py
  - tests/hermes_cli/test_timeouts.py
  - tests/run_agent/test_api_recovery_strategy.py
  - tests/cli/test_cli_api_recovery_probe.py
  - tests/cli/test_cli_status_bar.py
---

# apirecover AI brief

## One-line summary

This branch upgrades Hermes API failure handling from a single coarse timeout to a layered recovery strategy:
streaming uses real provider activity, non-streaming uses provider/model/context-aware stale timeout selection, and recoverable transport failures can trigger a visible `?` recovery probe in the CLI.

## Must-know concepts

- Streaming is activity-based, not wall-clock-based.
- Non-streaming stale timeout is resolved in layers:
  1. model override
  2. provider override
  3. env override
  4. context-bucket default
  5. `300s` final fallback
- Context buckets: `small`, `medium`, `large`, `huge`, `unknown`.
- Recovery state labels are explicit:
  - `transport_failure[recovery_pending]`
  - `transport_failure[recovered]`
  - `transport_failure[recovery_failed]`
- CLI only auto-queues `?` if the failure is visible and the user has not already queued an interrupt message.

## Before vs after

### Before
- Streaming and non-streaming recovery were not clearly separated.
- Non-streaming stale handling behaved like a more generic fixed-timeout problem.
- Recoverable transport failures were not surfaced as a first-class recovery state.
- The CLI had no explicit `?` recovery probe lane.

### After
- Streaming waits for real activity before considering a call stale.
- Non-streaming chooses stale timeout from config + context bucket.
- Recovery states are machine-readable and visible.
- The CLI can queue exactly one `?` probe when it is safe to do so.

## Invariants to preserve

1. Do not collapse all timeout logic back into one global constant.
2. Do not let the CLI auto-probe if the user already has an interrupt message pending.
3. Do not expose secrets in lifecycle or recovery messages.
4. Do not treat recoverable transport failures as opaque generic errors.
5. Keep recovery status labels stable unless tests are updated together.

## Where to look in code

- `run_agent.py`
  - stale timeout resolution
  - streaming activity tracking
  - recovery state emission
- `cli.py`
  - lifecycle status tracking
  - auto `?` probe queueing
- `hermes_cli/plugins.py`
  - `select_api_stale_timeout` hook
- `tests/hermes_cli/test_timeouts.py`
  - timeout precedence and fallback behavior
- `tests/run_agent/test_api_recovery_strategy.py`
  - stale counter and recovery labels
- `tests/cli/test_cli_api_recovery_probe.py`
  - `?` probe gating
- `tests/cli/test_cli_status_bar.py`
  - visible operator/status truthfulness

## Fast mental model

Think of the branch as three layers:

1. Detect whether the call is actually stale.
2. Decide whether the failure can recover automatically.
3. If yes, make that recovery visible to the CLI and operator.

## If you only check one thing

Read the spec first, then inspect the four code touchpoints:
`run_agent.py`, `cli.py`, `hermes_cli/plugins.py`, and the timeout/recovery tests.

## What future work usually looks like

This branch should mostly need small adjustments:
- tweak timeout buckets
- adjust recovery messages
- extend tests for a new provider/model
- refine CLI probe behavior

It should not need a redesign unless the provider API shape changes substantially.
