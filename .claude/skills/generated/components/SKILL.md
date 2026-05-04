---
name: components
description: "Skill for the Components area of hermes-agent. 107 symbols across 23 files."
---

# Components

107 symbols | 23 files | Cohesion: 86%

## When to Use

- Working with code in `ui-tui/`
- Understanding how lineNav, TextInput, flushParentChange work
- Modifying components-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `ui-tui/src/components/textInput.tsx` | graphemeStops, snapPos, prevPos, nextPos, wordLeft (+23) |
| `ui-tui/src/components/agentsOverlay.tsx` | formatRowId, statusGlyph, OverlayScrollbar, GanttStrip, Detail (+9) |
| `ui-tui/src/components/thinking.tsx` | nextTreeRails, TreeRow, TreeTextRow, TreeNode, Detail (+8) |
| `ui-tui/src/components/markdown.tsx` | renderMath, splitRow, isTableDivider, renderAutolink, stripInlineMarkup (+5) |
| `web/src/components/ModelPickerDialog.tsx` | onClose, onKey, confirm, ProviderColumn, onSelect (+2) |
| `web/src/components/ThemeSwitcher.tsx` | ThemeSwitcher, close, ThemeSwatch, PlaceholderSwatch |
| `ui-tui/packages/hermes-ink/src/ink/components/App.tsx` | App, isRawModeSupported, componentWillUnmount, resumeHandler |
| `web/src/App.tsx` | App, SidebarNavLink, SidebarSystemActions |
| `web/src/components/Markdown.tsx` | Markdown, Block, InlineContent |
| `ui-tui/src/components/branding.tsx` | ArtLines, SessionPanel, section |

## Entry Points

Start here when exploring this area:

- **`lineNav`** (Function) — `ui-tui/src/components/textInput.tsx:145`
- **`TextInput`** (Function) — `ui-tui/src/components/textInput.tsx:233`
- **`flushParentChange`** (Function) — `ui-tui/src/components/textInput.tsx:393`
- **`canFastEchoBase`** (Function) — `ui-tui/src/components/textInput.tsx:436`
- **`canFastAppend`** (Function) — `ui-tui/src/components/textInput.tsx:438`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `App` | Class | `ui-tui/packages/hermes-ink/src/ink/components/App.tsx` | 118 |
| `lineNav` | Function | `ui-tui/src/components/textInput.tsx` | 145 |
| `TextInput` | Function | `ui-tui/src/components/textInput.tsx` | 233 |
| `flushParentChange` | Function | `ui-tui/src/components/textInput.tsx` | 393 |
| `canFastEchoBase` | Function | `ui-tui/src/components/textInput.tsx` | 436 |
| `canFastAppend` | Function | `ui-tui/src/components/textInput.tsx` | 438 |
| `canFastBackspace` | Function | `ui-tui/src/components/textInput.tsx` | 451 |
| `commit` | Function | `ui-tui/src/components/textInput.tsx` | 459 |
| `swap` | Function | `ui-tui/src/components/textInput.tsx` | 510 |
| `emitPaste` | Function | `ui-tui/src/components/textInput.tsx` | 521 |
| `flushPaste` | Function | `ui-tui/src/components/textInput.tsx` | 552 |
| `clearSel` | Function | `ui-tui/src/components/textInput.tsx` | 569 |
| `moveCursor` | Function | `ui-tui/src/components/textInput.tsx` | 592 |
| `selRange` | Function | `ui-tui/src/components/textInput.tsx` | 608 |
| `pastePlainText` | Function | `ui-tui/src/components/textInput.tsx` | 618 |
| `startMouseSelection` | Function | `ui-tui/src/components/textInput.tsx` | 636 |
| `dragMouseSelection` | Function | `ui-tui/src/components/textInput.tsx` | 646 |
| `endMouseSelection` | Function | `ui-tui/src/components/textInput.tsx` | 659 |
| `App` | Function | `web/src/App.tsx` | 298 |
| `useSidebarStatus` | Function | `web/src/hooks/useSidebarStatus.ts` | 10 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `TextInput → Seg` | cross_community | 6 |
| `TextInput → CancelLocalRender` | intra_community | 4 |
| `TextInput → ScheduleLocalRender` | intra_community | 4 |
| `TextInput → FlushParentChange` | intra_community | 4 |
| `App → _notify` | cross_community | 4 |
| `App → GetPluginComponent` | cross_community | 4 |
| `TextInput → IsPasteResultPromise` | intra_community | 3 |
| `TextInput → SelRange` | intra_community | 3 |
| `AgentsOverlay → GuardLive` | cross_community | 3 |
| `AgentsOverlay → Interrupt` | cross_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Pages | 18 calls |
| Plugins | 1 calls |

## How to Explore

1. `gitnexus_context({name: "lineNav"})` — see callers and callees
2. `gitnexus_query({query: "components"})` — find related execution flows
3. Read key files listed above for implementation details
