---
type: architecture
layer: test
status: active
tags:
  - test
---

# Frontend Tests

Vitest + Testing Library + jsdom. Run: `npm test -- --run` (frontend dir). Setup in `frontend/src/test/setup.ts` (jest-dom, ResizeObserver/matchMedia stubs for the virtualizer and theme system).

| Suite | Covers |
|---|---|
| [[frontend.src.mail.MailWorkspace.test]] | Primary default, Inbox/All Mail switching, kind filters, category switching, empty states, global search scope, selection → reader + intelligence, Later persistence, backfill status states |
| [[frontend.src.mail.CategoryTabs.test]] | five tabs, live counts, switching |
| [[frontend.src.layout.WorkspaceHeader.test]] | Ctrl/Cmd+K focus, Escape blur, value propagation |
| [[frontend.src.theme.themeStore.test]] | persistence, system resolution, invalid stored values |
| [[frontend.src.theme.ThemeProvider.test]] | switching, persistence across mounts, system mode |
| `frontend/tests/app.test.tsx` | rail/status render, Overview content, Mail-as-default navigation, briefing fallback |
| `frontend/tests/priority.test.ts` | API priority contract |

## Related

- [[Testing Strategy]]
- [[Frontend Overview]]
