---
name: app
description: "Skill for the App area of hermes-agent. 63 symbols across 7 files."
---

# App

63 symbols | 7 files | Cohesion: 80%

## When to Use

- Working with code in `ui-tui/`
- Understanding how createGatewayEventHandler, scheduleThinkingStatus, restoreStatusAfter work
- Modifying app-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `ui-tui/src/app/turnController.ts` | parseTodos, flushStreamingSegment, recordTodos, pushInlineDiffSegment, recordToolComplete (+24) |
| `ui-tui/src/app/createGatewayEventHandler.ts` | statusFromBusy, applySkin, createGatewayEventHandler, scheduleThinkingStatus, restoreStatusAfter (+3) |
| `ui-tui/src/app/useSubmission.ts` | send, startSubmit, shellExec, interpolate, sendQueued (+2) |
| `ui-tui/src/app/useMainApp.ts` | appendMessage, sys, rpc, answerClarify, paste (+1) |
| `ui-tui/src/app/useSessionLifecycle.ts` | usageFrom, closeSession, resumeById, writeActiveSessionFile, resetSession (+1) |
| `ui-tui/src/app/useConfigSync.ts` | normalizeMouseTracking, quietRpc, applyDisplay, useConfigSync, id |
| `ui-tui/src/app/turnStore.ts` | patchTurnState, archiveTodosAtTurnEnd |

## Entry Points

Start here when exploring this area:

- **`createGatewayEventHandler`** (Function) — `ui-tui/src/app/createGatewayEventHandler.ts:55`
- **`scheduleThinkingStatus`** (Function) — `ui-tui/src/app/createGatewayEventHandler.ts:127`
- **`restoreStatusAfter`** (Function) — `ui-tui/src/app/createGatewayEventHandler.ts:140`
- **`isTerminalStatus`** (Function) — `ui-tui/src/app/createGatewayEventHandler.ts:151`
- **`keepTerminalElseRunning`** (Function) — `ui-tui/src/app/createGatewayEventHandler.ts:153`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `createGatewayEventHandler` | Function | `ui-tui/src/app/createGatewayEventHandler.ts` | 55 |
| `scheduleThinkingStatus` | Function | `ui-tui/src/app/createGatewayEventHandler.ts` | 127 |
| `restoreStatusAfter` | Function | `ui-tui/src/app/createGatewayEventHandler.ts` | 140 |
| `isTerminalStatus` | Function | `ui-tui/src/app/createGatewayEventHandler.ts` | 151 |
| `keepTerminalElseRunning` | Function | `ui-tui/src/app/createGatewayEventHandler.ts` | 153 |
| `handleReady` | Function | `ui-tui/src/app/createGatewayEventHandler.ts` | 155 |
| `send` | Function | `ui-tui/src/app/useSubmission.ts` | 86 |
| `startSubmit` | Function | `ui-tui/src/app/useSubmission.ts` | 90 |
| `shellExec` | Function | `ui-tui/src/app/useSubmission.ts` | 150 |
| `interpolate` | Function | `ui-tui/src/app/useSubmission.ts` | 179 |
| `sendQueued` | Function | `ui-tui/src/app/useSubmission.ts` | 200 |
| `handleBusyInput` | Function | `ui-tui/src/app/useSubmission.ts` | 228 |
| `dispatchSubmission` | Function | `ui-tui/src/app/useSubmission.ts` | 283 |
| `appendMessage` | Function | `ui-tui/src/app/useMainApp.ts` | 298 |
| `sys` | Function | `ui-tui/src/app/useMainApp.ts` | 303 |
| `rpc` | Function | `ui-tui/src/app/useMainApp.ts` | 333 |
| `answerClarify` | Function | `ui-tui/src/app/useMainApp.ts` | 420 |
| `paste` | Function | `ui-tui/src/app/useMainApp.ts` | 458 |
| `respondWith` | Function | `ui-tui/src/app/useMainApp.ts` | 656 |
| `normalizeMouseTracking` | Function | `ui-tui/src/app/useConfigSync.ts` | 67 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `DispatchSubmission → IsSessionBusyError` | intra_community | 5 |
| `AnswerClarify → CapHistory` | intra_community | 5 |
| `DispatchSubmission → SpliceMatches` | intra_community | 4 |
| `DispatchSubmission → ExpandSnips` | intra_community | 4 |
| `UseConfigSync → HasOwn` | intra_community | 4 |
| `RecordMessageComplete → Clear` | cross_community | 4 |
| `CreateGatewayEventHandler → ApplySkin` | intra_community | 3 |
| `CreateGatewayEventHandler → StatusFromBusy` | intra_community | 3 |
| `DispatchSubmission → Fallback` | intra_community | 3 |
| `DispatchSubmission → ShellExec` | intra_community | 3 |

## How to Explore

1. `gitnexus_context({name: "createGatewayEventHandler"})` — see callers and callees
2. `gitnexus_query({query: "app"})` — find related execution flows
3. Read key files listed above for implementation details
