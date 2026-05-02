---
branch: auth
purpose: keep same-session account selection sticky across main and auxiliary routing
read_first: README.md
spec: null
plan: null
primary_files:
  - cli.py
  - run_agent.py
  - hermes_cli/runtime_provider.py
  - agent/auxiliary_client.py
  - tests/cli/test_cli_provider_resolution.py
  - tests/agent/test_auxiliary_main_first.py
  - tests/agent/test_codex_cloudflare_headers.py
---

# auth AI brief

## One-line summary

This branch fixes the bug where appending to the same session would keep reselecting the highest-priority account instead of preserving the already-bound session credential.

## Must-know concepts

- Session-bound runtime credential: once a session has a usable credential, later turns should reuse it.
- Main vs auxiliary routing: `cli.py` / `run_agent.py` handle the primary conversation, while `agent/auxiliary_client.py` handles compression, titles, and similar side calls.
- Repo mirror vs installed runtime: changes were synchronized across `/Users/rain/hermes-agent` and `/Users/rain/dev/-github/hermes-agent-auth`, but `~/.hermes` remains a separate installed profile.

## Before vs after

### Before

- CLI active-session handling was sticky only on the surface.
- `openai-codex` auxiliary routing could still reload the pool and call `select()` again.
- Same-session append could jump back to the top-ranked account.

### After

- Active sessions keep the bound pool credential.
- `main_runtime` carries the current credential into auxiliary routing.
- `resolve_provider_client("openai-codex", ...)` prefers explicit runtime credentials and does not force pool reselection.

## Invariants to preserve

1. Same session append must not reselect the top-ranked account unless there is a real failover.
2. New sessions may still start from the normal priority order.
3. Auxiliary tasks must inherit the same session credential semantics as the main turn.

## Where to look in code

- `cli.py` — session credential stickiness and runtime refresh flow.
- `run_agent.py` — propagates live main runtime into auxiliary calls.
- `hermes_cli/runtime_provider.py` — builds the runtime dict passed around the app.
- `agent/auxiliary_client.py` — the main fix for openai-codex explicit runtime credentials.
- `tests/cli/test_cli_provider_resolution.py` — regression for active-session stickiness.
- `tests/agent/test_auxiliary_main_first.py` / `tests/agent/test_codex_cloudflare_headers.py` — auxiliary routing regressions.

## Fast mental model

Think of the session as owning one runtime credential until it genuinely fails. The bug was that the auxiliary path treated every turn like a fresh lookup and silently picked the best-ranked account again.

## Verification

- `scripts/run_tests.sh tests/cli/test_cli_provider_resolution.py::test_active_session_keeps_bound_pool_credential_instead_of_reselecting_top -q`: pass
- `scripts/run_tests.sh tests/agent/test_auxiliary_main_first.py::TestResolveAutoMainFirst tests/agent/test_codex_cloudflare_headers.py -q`: pass
- Direct hermetic `python -m pytest` in the auth worktree using `/Users/rain/hermes-agent/venv`: pass

## Future work usually looks like

- Propagate sticky runtime credentials into any new auxiliary route.
- Add regression tests whenever a new provider path might re-open pool reselection.
- Keep distinguishing branch-local repo edits from installed-profile state under `~/.hermes`.
