---
type: architecture
layer: frontend
status: active
tags:
  - frontend
  - architecture
---

# Frontend Code Map

Human-readable map of the frontend source tree (`frontend/src/`).

| Path | Contents |
|---|---|
| `main.tsx` | Providers (Theme → Query) → App |
| `App.tsx` | Page state, ambient layer, rail/header composition, sync mutation |
| `api/client.ts` | `api()` fetch wrapper (base from `VITE_ALFRED_API_URL`) |
| `api/emails.ts` | Typed endpoints: emails/counts/accounts/sync/backfill/tasks/briefing/draft/health |
| `layout/IconRail.tsx` | Rail nav + labelled connection status |
| `layout/WorkspaceHeader.tsx` | Header, global search (Ctrl+K), AI chip, avatar |
| `mail/MailWorkspace.tsx` | The workspace: views, kinds, categories, filters, backfill observation, Later state |
| `mail/CategoryTabs.tsx` | Gmail tab navigation with live counts |
| `mail/MessageList.tsx` | Virtualized list |
| `mail/MessageRow.tsx` | Row rendering, badges, quick actions |
| `mail/MessageReader.tsx` | Document reader + toolbar (Later/Copy/Intel) |
| `intelligence/IntelligencePanel.tsx` | AI companion pane + draft |
| `features/*` | Overview / Tasks / Deadlines / Accounts / Settings pages |
| `components/ui/AnalysisProgress.tsx` | SSE progress pill |
| `theme/*` | ThemeProvider, ThemeToggle, themeStore |
| `styles/*.css` | tokens → themes → motion → surfaces → globals → reset |
| `test/setup.ts` | Vitest environment shims |

## Related

- [[Frontend Overview]]
- [[Frontend Component Map]]
- [[Entry Points]]
