# API Recovery Strategy Specification

## Purpose

Implement a complete API recovery policy for Hermes Agent so stalled provider calls are handled by the right recovery lane instead of waiting for a single fixed timeout.

The final behavior must separate streaming and non-streaming traffic, use provider/model configuration when explicit, select context-bucket defaults when no explicit timeout is configured, and surface recoverable transport failures in a way the CLI can immediately queue a `?` recovery probe.

## Required final behavior

### 1. Streaming requests use provider activity

Streaming requests must be judged by provider activity, not by elapsed time since request start.

Required behavior:

- Chat-completions and Anthropic streaming keep their existing real-chunk activity clock.
- Codex Responses streaming must mark provider activity for text deltas, reasoning deltas, completed response output items, and stream fallback deltas.
- A stream is stale only when no real provider activity has happened for the configured streaming stale timeout.
- Local endpoints keep the current safety behavior: implicit streaming stale timeout is disabled unless explicitly configured.

### 2. Non-streaming requests use provider/model plus context bucket policy

Non-streaming requests must not treat 300 seconds as the universal wait.

Required priority:

1. `providers.<provider>.models.<model>.stale_timeout_seconds`
2. `providers.<provider>.stale_timeout_seconds`
3. `HERMES_API_CALL_STALE_TIMEOUT`
4. context-bucket implicit policy
5. 300 seconds only as a final unknown-bucket fallback

Context buckets:

- `small`: estimated context below 16k tokens, implicit stale timeout 90 seconds
- `medium`: 16k to below 50k tokens, implicit stale timeout 120 seconds
- `large`: 50k to below 100k tokens, implicit stale timeout 180 seconds
- `huge`: 100k tokens or more, implicit stale timeout 210 seconds
- `unknown`: fallback 300 seconds

Explicit provider/model/env stale timeout values must be honored without being raised by context-bucket defaults. Local endpoints keep their existing safety behavior: when no stale timeout is explicit, non-stream stale detection is disabled.

### 3. Hook seam for user policy

The core must expose a `select_api_stale_timeout` plugin hook.

Hook payload must contain only non-secret metadata:

- provider
- model
- api_mode
- base legacy timeout seconds
- effective context bucket
- estimated context tokens
- whether the timeout came from implicit policy
- non-stream stale timeout count for this agent
- whether the request appears to be a long-output request
- long-output indicator labels only

Hook return values:

- numeric seconds
- dictionary containing `stale_timeout_seconds`
- invalid/malformed values fail closed to the legacy timeout

### 4. Non-stream stale count

The agent must track `_non_stream_stale_timeout_count`.

Required behavior:

- Increment when a non-streaming call is killed by stale timeout.
- Do not reset on transport errors or stale kills.
- Reset only after a successful non-streaming response.

### 5. Recoverable transport failure status

Recoverable transport failures must emit visible status labels:

- `transport_failure[recovery_pending]`
- `transport_failure[recovered]`
- `transport_failure[recovery_failed]`

The message must include the reason label `visible_transport_auto_recovery` and enough non-secret context for the CLI/operator to understand the recovery lane.

### 6. CLI `?` recovery probe

When the CLI observes `transport_failure[recovery_pending]` from the active agent and the user has not already queued an interrupt message, it must queue a single `?` as the next prompt after the current agent thread ends.

Required behavior:

- The probe is queued once per visible recoverable failure burst.
- User-provided interrupt messages always take priority over the automatic probe.
- `queue` and `steer` busy-input modes keep their documented semantics.
- The probe mechanism must be deterministic and covered by unit tests.

## Verification requirements

The implementation is complete only when:

- New tests prove context-bucket timeout selection.
- New tests prove plugin hook registration and fail-closed parsing.
- New tests prove Codex Responses request metadata uses `input`, `instructions`, and `tools`, not only `messages`.
- New tests prove stream activity callback updates on reasoning/text deltas.
- New tests prove stale count increments and resets only after success.
- New tests prove transport recovery labels are emitted.
- New tests prove the CLI queues `?` after a visible recoverable failure and does not override user interrupt input.
- Targeted tests pass through the project test harness.
