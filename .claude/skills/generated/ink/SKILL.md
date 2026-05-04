---
name: ink
description: "Skill for the Ink area of hermes-agent. 121 symbols across 20 files."
---

# Ink

121 symbols | 20 files | Cohesion: 87%

## When to Use

- Working with code in `ui-tui/`
- Understanding how selectionBounds, getSelectedText, captureScrolledRows work
- Modifying ink-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `ui-tui/packages/hermes-ink/src/ink/ink.tsx` | copySelection, notifySelectionChange, handleSelectionDrag, applySelectionDrag, updateSelectionAutoScroll (+20) |
| `ui-tui/packages/hermes-ink/src/ink/screen.ts` | transition, intern, get, withInverse, withCurrentMatch (+11) |
| `ui-tui/packages/hermes-ink/src/ink/selection.ts` | selectionBounds, selectionContentBounds, extractRowText, getSelectedText, captureScrolledRows (+8) |
| `ui-tui/packages/hermes-ink/src/ink/output.ts` | blit, clear, write, clip, unclip (+6) |
| `ui-tui/packages/hermes-ink/src/ink/log-update.ts` | render, transitionHyperlink, transitionStyle, fullResetSequence_CAUSES_FLICKER, renderFrame (+5) |
| `ui-tui/packages/hermes-ink/src/ink/dom.ts` | appendChildNode, insertBeforeNode, removeChildNode, markDirty, setTextNodeValue (+4) |
| `ui-tui/packages/hermes-ink/src/ink/render-node-to-output.ts` | wrapWithOsc8Link, applyStylesToWrappedText, renderNodeToOutput, renderChildren, blitEscapingAbsoluteDescendants (+2) |
| `ui-tui/packages/hermes-ink/src/ink/parse-keypress.ts` | parseTerminalResponse, parseMultipleKeypresses, parseMouseEvent, parseSgrMouseFragment, parseTextWithSgrMouseFragments (+1) |
| `ui-tui/packages/hermes-ink/src/ink/wrap-text.ts` | memoizedWrap, truncate, computeWrap, wrapText |
| `ui-tui/packages/hermes-ink/src/ink/reconciler.ts` | setEventHandler, applyProp, commitUpdate |

## Entry Points

Start here when exploring this area:

- **`selectionBounds`** (Function) — `ui-tui/packages/hermes-ink/src/ink/selection.ts:819`
- **`getSelectedText`** (Function) — `ui-tui/packages/hermes-ink/src/ink/selection.ts:969`
- **`captureScrolledRows`** (Function) — `ui-tui/packages/hermes-ink/src/ink/selection.ts:1015`
- **`applySelectionOverlay`** (Function) — `ui-tui/packages/hermes-ink/src/ink/selection.ts:1107`
- **`transform`** (Function) — `ui-tui/packages/hermes-ink/src/ink/render-to-screen.ts:222`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `Ink` | Class | `ui-tui/packages/hermes-ink/src/ink/ink.tsx` | 141 |
| `selectionBounds` | Function | `ui-tui/packages/hermes-ink/src/ink/selection.ts` | 819 |
| `getSelectedText` | Function | `ui-tui/packages/hermes-ink/src/ink/selection.ts` | 969 |
| `captureScrolledRows` | Function | `ui-tui/packages/hermes-ink/src/ink/selection.ts` | 1015 |
| `applySelectionOverlay` | Function | `ui-tui/packages/hermes-ink/src/ink/selection.ts` | 1107 |
| `transform` | Function | `ui-tui/packages/hermes-ink/src/ink/render-to-screen.ts` | 222 |
| `parseMultipleKeypresses` | Function | `ui-tui/packages/hermes-ink/src/ink/parse-keypress.ts` | 219 |
| `renderSync` | Function | `ui-tui/packages/hermes-ink/src/ink/root.ts` | 90 |
| `createRenderer` | Function | `ui-tui/packages/hermes-ink/src/ink/renderer.ts` | 32 |
| `renderToScreen` | Function | `ui-tui/packages/hermes-ink/src/ink/render-to-screen.ts` | 58 |
| `appendChildNode` | Function | `ui-tui/packages/hermes-ink/src/ink/dom.ts` | 128 |
| `insertBeforeNode` | Function | `ui-tui/packages/hermes-ink/src/ink/dom.ts` | 143 |
| `removeChildNode` | Function | `ui-tui/packages/hermes-ink/src/ink/dom.ts` | 187 |
| `markDirty` | Function | `ui-tui/packages/hermes-ink/src/ink/dom.ts` | 422 |
| `setTextNodeValue` | Function | `ui-tui/packages/hermes-ink/src/ink/dom.ts` | 463 |
| `useInputHandlers` | Function | `ui-tui/src/app/useInputHandlers.ts` | 26 |
| `wrapText` | Function | `ui-tui/packages/hermes-ink/src/ink/wrap-text.ts` | 102 |
| `clearSelection` | Function | `ui-tui/packages/hermes-ink/src/ink/selection.ts` | 118 |
| `shiftSelection` | Function | `ui-tui/packages/hermes-ink/src/ink/selection.ts` | 579 |
| `shift` | Function | `ui-tui/packages/hermes-ink/src/ink/selection.ts` | 645 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Termio | 1 calls |

## How to Explore

1. `gitnexus_context({name: "selectionBounds"})` — see callers and callees
2. `gitnexus_query({query: "ink"})` — find related execution flows
3. Read key files listed above for implementation details
