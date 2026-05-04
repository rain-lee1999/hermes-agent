<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **hermes-agent** (112456 symbols, 191244 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/hermes-agent/context` | Codebase overview, check index freshness |
| `gitnexus://repo/hermes-agent/clusters` | All functional areas |
| `gitnexus://repo/hermes-agent/processes` | All execution flows |
| `gitnexus://repo/hermes-agent/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |
| Work in the Tools area (2208 symbols) | `.claude/skills/generated/tools/SKILL.md` |
| Work in the Hermes_cli area (1994 symbols) | `.claude/skills/generated/hermes-cli/SKILL.md` |
| Work in the Gateway area (1928 symbols) | `.claude/skills/generated/gateway/SKILL.md` |
| Work in the Agent area (989 symbols) | `.claude/skills/generated/agent/SKILL.md` |
| Work in the Platforms area (925 symbols) | `.claude/skills/generated/platforms/SKILL.md` |
| Work in the Scripts area (488 symbols) | `.claude/skills/generated/scripts/SKILL.md` |
| Work in the Run_agent area (387 symbols) | `.claude/skills/generated/run-agent/SKILL.md` |
| Work in the Tests area (246 symbols) | `.claude/skills/generated/tests/SKILL.md` |
| Work in the Cron area (157 symbols) | `.claude/skills/generated/cron/SKILL.md` |
| Work in the Environments area (146 symbols) | `.claude/skills/generated/environments/SKILL.md` |
| Work in the Ink area (121 symbols) | `.claude/skills/generated/ink/SKILL.md` |
| Work in the Tui_gateway area (118 symbols) | `.claude/skills/generated/tui-gateway/SKILL.md` |
| Work in the Cli area (115 symbols) | `.claude/skills/generated/cli/SKILL.md` |
| Work in the Components area (107 symbols) | `.claude/skills/generated/components/SKILL.md` |
| Work in the Pages area (95 symbols) | `.claude/skills/generated/pages/SKILL.md` |
| Work in the Honcho area (83 symbols) | `.claude/skills/generated/honcho/SKILL.md` |
| Work in the Plugins area (68 symbols) | `.claude/skills/generated/plugins/SKILL.md` |
| Work in the Integration area (67 symbols) | `.claude/skills/generated/integration/SKILL.md` |
| Work in the App area (63 symbols) | `.claude/skills/generated/app/SKILL.md` |
| Work in the Acp_adapter area (62 symbols) | `.claude/skills/generated/acp-adapter/SKILL.md` |

<!-- gitnexus:end -->
