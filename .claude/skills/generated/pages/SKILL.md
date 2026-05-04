---
name: pages
description: "Skill for the Pages area of hermes-agent. 95 symbols across 39 files."
---

# Pages

95 symbols | 39 files | Cohesion: 84%

## When to Use

- Working with code in `web/`
- Understanding how getSlotEntries, PluginSlot, useToast work
- Modifying pages-related functionality

## Key Files

| File | Symbols |
|------|---------|
| `web/src/pages/ModelsPage.tsx` | formatTokens, formatCost, TokenBar, UseAsMenu, assign (+5) |
| `web/src/pages/AnalyticsPage.tsx` | formatTokens, formatDate, useTableSort, SortHeader, TokenBarChart (+4) |
| `web/src/pages/PluginsPage.tsx` | PluginsPage, PluginRowCard, loadHub, onInstall, onRescan (+2) |
| `web/src/pages/ChatPage.tsx` | ChatPage, terminalTierWidthPx, terminalFontSizeForWidth, terminalLineHeightForWidth, scheduleHostSync (+1) |
| `web/src/pages/SessionsPage.tsx` | SessionRow, SessionsPage, ToolCallBlock, MessageBubble, MessageList |
| `web/src/pages/ConfigPage.tsx` | ConfigPage, CategoryIcon, prettyCategoryName, handleReset, renderFields |
| `web/src/components/ui/card.tsx` | Card, CardHeader, CardTitle, CardDescription, CardContent |
| `web/src/pages/EnvPage.tsx` | EnvVarRow, ProviderGroupCard, EnvPage, CollapsibleUnset |
| `web/src/pages/CronPage.tsx` | CronPage, loadJobs, handlePauseResume, handleTrigger |
| `web/src/pages/SkillsPage.tsx` | prettyCategory, SkillsPage, PanelItem |

## Entry Points

Start here when exploring this area:

- **`getSlotEntries`** (Function) — `web/src/plugins/slots.ts:137`
- **`PluginSlot`** (Function) — `web/src/plugins/slots.ts:176`
- **`useToast`** (Function) — `web/src/hooks/useToast.ts:2`
- **`useConfirmDelete`** (Function) — `web/src/hooks/useConfirmDelete.ts:2`
- **`cn`** (Function) — `web/src/lib/utils.ts:3`

## Key Symbols

| Symbol | Type | File | Line |
|--------|------|------|------|
| `getSlotEntries` | Function | `web/src/plugins/slots.ts` | 137 |
| `PluginSlot` | Function | `web/src/plugins/slots.ts` | 176 |
| `useToast` | Function | `web/src/hooks/useToast.ts` | 2 |
| `useConfirmDelete` | Function | `web/src/hooks/useConfirmDelete.ts` | 2 |
| `cn` | Function | `web/src/lib/utils.ts` | 3 |
| `timeAgo` | Function | `web/src/lib/utils.ts` | 8 |
| `formatTokenCount` | Function | `web/src/lib/format.ts` | 4 |
| `usePageHeader` | Function | `web/src/contexts/usePageHeader.ts` | 3 |
| `PluginPage` | Function | `web/src/plugins/PluginPage.tsx` | 12 |
| `SkillsPage` | Function | `web/src/pages/SkillsPage.tsx` | 95 |
| `SessionsPage` | Function | `web/src/pages/SessionsPage.tsx` | 411 |
| `ProfilesPage` | Function | `web/src/pages/ProfilesPage.tsx` | 20 |
| `load` | Function | `web/src/pages/ProfilesPage.tsx` | 43 |
| `handleRenameSubmit` | Function | `web/src/pages/ProfilesPage.tsx` | 78 |
| `PluginsPage` | Function | `web/src/pages/PluginsPage.tsx` | 25 |
| `ModelsPage` | Function | `web/src/pages/ModelsPage.tsx` | 641 |
| `LogsPage` | Function | `web/src/pages/LogsPage.tsx` | 48 |
| `EnvPage` | Function | `web/src/pages/EnvPage.tsx` | 487 |
| `DocsPage` | Function | `web/src/pages/DocsPage.tsx` | 17 |
| `CronPage` | Function | `web/src/pages/CronPage.tsx` | 33 |

## Execution Flows

| Flow | Type | Steps |
|------|------|-------|
| `RenderFields → Cn` | cross_community | 4 |
| `SkillsPage → Cn` | intra_community | 3 |
| `ConfigPage → Cn` | intra_community | 3 |
| `LogsPage → Cn` | intra_community | 3 |
| `DocsPage → GetSlotEntries` | intra_community | 3 |
| `DocsPage → OnSlotRegistered` | intra_community | 3 |
| `ModelCard → Cn` | intra_community | 3 |
| `OAuthProvidersCard → Cn` | intra_community | 3 |

## Connected Areas

| Area | Connections |
|------|-------------|
| Components | 8 calls |
| Plugins | 1 calls |

## How to Explore

1. `gitnexus_context({name: "getSlotEntries"})` — see callers and callees
2. `gitnexus_query({query: "pages"})` — find related execution flows
3. Read key files listed above for implementation details
