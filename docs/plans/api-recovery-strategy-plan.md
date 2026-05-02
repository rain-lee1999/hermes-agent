# API Recovery Strategy Implementation Plan

## Scope

Repository: `/Users/rain/dev/-github/hermes-agent-apirecover`

Deliver a complete, tested implementation of the API recovery strategy described in `docs/specs/api-recovery-strategy.md`.

## Execution sequence

### 1. Bound the source surface

Inspect and modify only these primary surfaces unless a test exposes a necessary adjacent change:

- `run_agent.py`
- `cli.py`
- `hermes_cli/plugins.py`
- `tests/hermes_cli/test_timeouts.py`
- `tests/run_agent/test_stream_interrupt_retry.py`
- `tests/cli/test_cli_retry.py` or a new focused CLI test file

### 2. Add failing tests first

Add regression tests for:

- `select_api_stale_timeout` is a valid hook.
- Context bucket implicit stale timeout values are 90/120/180/210 and unknown falls back to 300.
- Explicit provider/model/env stale timeout is honored ahead of context-bucket policy.
- Codex Responses stats count `input`, `instructions`, and `tools` when `messages` is absent.
- Hook numeric and dict return values override legacy timeout.
- Hook invalid values fall back to legacy timeout.
- Hook payload contains labels and counts but not raw request text.
- Codex stream text/reasoning deltas call the stream activity callback.
- Non-stream stale timeout count increments on stale kill and resets after successful non-stream response.
- Visible transport recovery status helper emits pending/recovered/failed labels.
- CLI auto-queues `?` exactly once after `transport_failure[recovery_pending]` when no user interrupt message exists.
- CLI does not queue `?` when a real user interrupt message is already pending.

### 3. Implement core timeout policy

In `run_agent.py`:

- Add `_non_stream_stale_timeout_count` initialization.
- Add `_non_stream_request_stats(api_kwargs_or_messages)`.
- Add `_context_bucket_for_estimated_tokens(tokens)`.
- Add `_implicit_non_stream_stale_timeout_for_bucket(bucket)`.
- Update `_compute_non_stream_stale_timeout` to accept full API kwargs, preserve backward compatibility for list inputs, honor explicit config/env values, then use context buckets, then fallback 300.
- Add `_parse_api_stale_timeout_hook_result`.
- Invoke `select_api_stale_timeout` with non-secret metadata.
- Increment stale count when the stale detector kills a non-streaming request.
- Reset stale count only when `_interruptible_api_call` returns a successful non-streaming response.

### 4. Implement stream activity truth

In `run_agent.py`:

- Add optional `on_stream_activity` to `_run_codex_stream` and `_run_codex_create_stream_fallback`.
- Call it on text deltas, reasoning deltas, completed output items, and fallback stream deltas.
- Pass an activity callback from the interruptible request wrapper so the stale detector measures from the last provider activity instead of request start for Codex Responses streams.

### 5. Implement visible recovery status

In `run_agent.py`:

- Add `_transport_recovery_state_label`.
- Add `_is_visible_recoverable_transport_failure`.
- Add `_emit_visible_transport_failure_status`.
- Emit `transport_failure[recovery_pending]` before automatic retry/recovery for recoverable timeout/server transport failures.
- Emit `transport_failure[recovered]` when a recovery lane is activated.
- Emit `transport_failure[recovery_failed]` before final failure after retry/fallback exhaustion.

### 6. Implement CLI recovery probe

In `cli.py`:

- Add active-agent status callback wiring.
- Track one pending automatic recovery probe per active turn.
- Queue `?` after the agent thread ends only if no user interrupt message is already queued.
- Preserve existing `interrupt`, `queue`, and `steer` behavior.

### 7. Verification harness

Run the focused project harness:

- `scripts/run_tests.sh tests/hermes_cli/test_timeouts.py`
- `scripts/run_tests.sh tests/run_agent/test_stream_interrupt_retry.py`
- focused CLI recovery probe tests

If the harness cannot run because the checkout lacks a virtualenv, use the repository-approved fallback pattern from `AGENTS.md`: activate an available repo venv or run the equivalent Python module command with CI-like environment variables, and record the exact command and result.

### 8. Final graph review

After source edits:

- Rebuild/update CRG.
- Run change detection.
- Run impact radius.
- Run affected flows or review context.
- Summarize exact files changed and verification results.
