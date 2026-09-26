# Alfred — UI Audit

Status: active
Date: 2026-09-26, Phase 1 priority 7
Scope: `frontend/src` and `frontend/src/styles`, as they existed before UI-1.

This is a factual inventory of the existing interface. It records what is there, what
works, and what is wrong — with `file:line` evidence. Proposals live in
`docs/UI-DESIGN-SPEC.md`; this document does not recommend.

---

## 1. Current layout

A CSS Grid application shell (`globals.css:11-21`):

```
grid-template-columns: var(--rail-width) 1fr;   /* 56px + rest */
grid-template-rows:    var(--header-height) 1fr; /* 52px + rest */
grid-template-areas:   'rail header' 'rail content';
```

`html, body, #root { height: 100%; overflow: hidden }` (`reset.css:6-9`). The document
never scrolls; every region manages its own overflow.

Inside `main.workspace-content` (`App.tsx:143`) the Mail view is a
`react-resizable-panels` horizontal `Group` (`MailWorkspace.tsx:275-282`) with three
panels — `mail`, `reader`, `intel` — separated by two `Separator` elements
(`:453`, `:466`). Default split is `{ mail: 30, reader: 45, intel: 25 }`
(`layoutStore.ts:31-35`), persisted to `localStorage` under `alfred-pane-layout-v2`
(`layoutStore.ts:22`) and validated on read with a 98–102 % sum window
(`layoutStore.ts:57-66`).

This is a good foundation. Three panes, a persisted validated layout, and a
container-query-driven responsive strategy are all correct decisions.

## 2. Current navigation

No router. `App.tsx:32` holds `useState<AppPage>('mail')`; six pages render
conditionally. The comment at `App.tsx:35-37` states this deliberately.

`IconRail` (`IconRail.tsx`) is a 56 px icon-only rail with two `<nav>` landmarks:

| Group | Items | Lines |
| --- | --- | --- |
| `aria-label="Alfred sections"` | Overview, Mail, Tasks, Deadlines | `:20-25` |
| `aria-label="System sections"` | Accounts, Settings | `:27-30` |

All six items are reachable and every one renders a real view. `aria-current="page"` is
set on the active item (`:98`).

**The product capabilities named in the brief, and where they currently live:**

| Capability | Current location | Assessment |
| --- | --- | --- |
| Inbox | `MailWorkspace` view switch, `:315-317` | working, pane-scoped |
| All Mail | `MailWorkspace` view switch, `:315-317` | working, pane-scoped |
| Overview | rail item | working |
| Important | `MailWorkspace` filter button, `:394-397` | working, pane-scoped |
| Needs Reply | `MailWorkspace` filter button, `:394-397` | working, pane-scoped |
| Tasks | rail item | working |
| Deadlines | rail item | working |
| Later | `MailWorkspace` filter button, `:394-397` | working, pane-scoped |
| Accounts | rail item | working |
| Settings | rail item | working |

**Every capability exists and works.** Nothing is dead. The real problem is that six of
the ten are unreachable from the rail — a user in the Tasks page cannot see the mail
filters, and a user in the rail cannot see what is filtered. The information is split
across two navigation surfaces that never show each other's state.

## 3. Existing components

17 audited files. Line counts are exact.

| File | Lines | Notes |
| --- | --- | --- |
| `mail/MailWorkspace.tsx` | 629 | largest component; 6 inline sub-components |
| `mail/MailWorkspace.test.tsx` | 540 | |
| `features/tasks/TasksPage.tsx` | 244 | |
| `mail/MessageReader.tsx` | 203 | |
| `features/overview/OverviewPage.tsx` | 196 | |
| `intelligence/IntelligencePanel.tsx` | 162 | |
| `mail/SourceEmailPreview.tsx` | 163 | |
| `features/accounts/AccountsPage.tsx` | 152 | |
| `App.tsx` | 182 | |
| `components/ui/AnalysisProgress.tsx` | 137 | |
| `mail/MessageRow.tsx` | 124 | |
| `features/settings/SettingsPage.tsx` | 119 | |
| `mail/CategoryTabs.tsx` | 90 | |
| `layout/WorkspaceHeader.tsx` | 86 | |
| `mail/MessageList.tsx` | 86 | |
| `mail/layoutStore.ts` | 85 | |
| `layout/IconRail.tsx` | 104 | |
| `layout/StartupGate.tsx` | rewritten in Phase 1 | |
| `mail/LinkifiedBody.tsx` | 83 | |
| `search/searchParser.ts` | 169 | |
| `theme/*` | 37–69 each | |
| `api/*` | 62 + 218 | |
| `lib/urlSecurity.ts` | 21 | |

## 4. Existing design tokens

`src/styles/tokens.css` (78 lines) plus `themes.css` (187). This is the strongest part
of the existing system and is preserved.

Theme-agnostic scales: motion (5 tokens), radii (6), spacing (4→40 px, 4 px base),
typography (8 sizes + 4 line-heights + 2 families), layout constants (4), blur (2),
z-index (6).

`themes.css` defines two complete 60-property sets, `:root[data-theme='light']` at
`:10-95` and `:root[data-theme='dark']` at `:101-186`, each with `color-scheme`.

A pre-paint inline script in `index.html` applies the stored theme before first paint,
so there is no theme flash. That is correct and is kept.

**Broken token references:** `styles.css:7` and `:9` map `--color-card` and
`--color-popover` to `var(--bg-elevated)`, and `--bg-elevated` is defined in no
stylesheet. Both resolve to nothing.

## 5. Existing Tailwind configuration

Present but inert.

- `@tailwindcss/vite` in `vite.config.ts`; `@import "tailwindcss"` at `styles.css:1`
- A 38-name `@theme inline` shadcn mapping at `styles.css:4-41`
- `components.json` declaring shadcn `new-york`, `cssVariables: true`
- `src/lib/utils.ts` exporting `cn()` = `twMerge(clsx(...))` — **imported by nothing**
- `class-variance-authority`, `clsx`, `tailwind-merge` as dependencies; `cva(` has zero
  call sites
- `sharp` and `png-to-ico` as devDependencies with zero references

**Zero Tailwind utility classes exist in the codebase.** Every `className` in every
non-test file is a hand-written semantic name. Tailwind's preflight is injected and then
overridden by `reset.css`, which performs its own margin/padding reset and its own
`button`/`input` normalisation. No shadcn component was ever generated;
`src/components/ui/` contains only `AnalysisProgress.tsx`.

## 6. Existing typography

`--font-sans` leads with `'Segoe UI Variable Text'` — the correct Windows-native choice.
**Zero webfont bytes ship.** `--font-mono` is Cascadia Code.

Scale: `--text-xs 11.5` / `sm 13` / `base 14` / `md 15.5` / `lg 17.5` / `xl 20` /
`2xl 23` / `3xl 27`. Leading: `tight 1.3` / `normal 1.5` / `relaxed 1.68` /
`reader 1.66`.

An 8-step scale with one ratio and a dedicated reader leading is a good system. It is
preserved.

**Arbitrary weights in use:** `font-weight: 650` on `.message-sender`
(`globals.css`, unread) and `700` on `.message-row.selected .message-sender`. 650 is not
a standard step; it works in Segoe UI Variable but is not in the documented scale, so
weight is currently an undocumented part of the type system.

## 7. Existing colour system

Accent: `--accent #6d5ae0` light, `#8b7bf5` dark, hue 248.5°.
Plus `--accent-hover`, `--accent-active`, `--accent-text`, `--accent-soft`,
`--shadow-accent`, `--border-focus`, `--unread-dot`.

Semantic: success, warning, danger, info, each with a `-soft` tint. Priority has its own
4-tier ramp (`--priority-{urgent,high,medium,low}-{bg,fg}`).

**Measured AA failures (Phase 1, `docs/Design.md` §3.1):**

| Token | Value | Worst surface | Ratio | Required |
| --- | --- | --- | --- | --- |
| `--text-muted` light | `#767e97` | `#f2f3f8` | 3.64 | 4.5 |
| `--text-faint` light | `#a0a7bd` | `#f2f3f8` | 2.16 | 4.5 |
| `--text-faint` dark | `#525c76` | `#151a24` | 2.61 | 4.5 |
| `--success` light | `#15936a` | `#f2f3f8` | 3.50 | 4.5 |
| `--warning` light | `#b07d1a` | `#f2f3f8` | 3.27 | 4.5 |
| `--info` light | `#2e7fd6` | `#f2f3f8` | 3.70 | 4.5 |
| `--danger` light | `#d04848` | `#f2f3f8` | 4.03 | 4.5 |

`--text-muted` carries message counts, timestamps, snippets and metadata;
`--text-faint` carries attachment labels. This is a release blocker.

**Accent headroom:** violet's worst case is 4.52 against `--bg-app` — **+0.02 over the
4.5 threshold.** Any future token nudge fails it. See ADR-005.

## 8. Existing icon system

One library: `lucide-react`, used across 30+ components, `size={18}` / `strokeWidth={2}`
in the rail. **Zero emoji anywhere.** One coherent icon language; no competing set.

The brand mark is a single `<img src="/alfred-icon.png">` with a literal letter `A`
fallback (`IconRail.tsx:46-54`). `icon.svg` in `desktop/src-tauri/icons/` is a third,
different, hand-authored artwork with an envelope-in-A motif that appears in no raster
file. `tools/generate_icons.py:1-8` declares in its own docstring that it generates a
placeholder.

## 9. Loading states

| Location | Mechanism |
| --- | --- |
| `MessageList.tsx:30-41` | 8 `skeleton-row` of 3 `skeleton` bars, `aria-busy="true"`, `aria-label="Loading messages"` |
| `MessageReader.tsx:102-119` | shaped skeleton mirroring the real layout (avatar + 2 bars + 3 lines) |
| `SourceEmailPreview.tsx:138-143` | 4 skeleton bars |
| `TasksPage.tsx:91-98`, `DeadlinesPage.tsx:25-32` | 5 / 4 `skeleton-row` |
| `AccountsPage.tsx:67-69` | 2 `skeleton` at height 84 |
| `MailWorkspace.tsx:421` | `RefreshCw.btn-spinner` when `isFetching` |
| `AnalysisProgress.tsx:119` | `progress-spinner` when working |

Consistent in mechanism, inconsistent in shape: each screen invents its own skeleton
proportions. All skeleton heights are inline `style` values, not tokens.

## 10. Empty states

`.empty-state` (`globals.css`) is a centred column: 30 px icon in a `--accent-soft`
rounded square, one sentence.

| Location | Message |
| --- | --- |
| `MessageList.tsx:48` | "No messages here." |
| `MessageReader.tsx:92` | "Select a message to read it." + icon |
| `TasksPage.tsx:101-102` | 3 variants by filter state |
| `DeadlinesPage.tsx:35` | icon + message |
| `AccountsPage.tsx:74-83` | message + **Connect Gmail** action |
| `IntelligencePanel.tsx:50-54` | "Analysis pending…" + spinner |
| `OverviewPage.tsx:108-110` | "overview-empty" paragraph |

`AccountsPage` is the only empty state that offers the action that fixes it. The
others describe the absence without offering the next step.

## 11. Error states

| Location | Behaviour |
| --- | --- |
| `MessageReader.tsx:95-101` | `.text-danger` + `.text-muted` explanation |
| `MailWorkspace.tsx:522` | `role="alert"` sync-failure report, dismissible |
| `MailWorkspace.tsx:140-167` | backfill failure with Pause/Retry |
| `AccountsPage.tsx:61-63` | `.banner.banner-danger` on connect error |
| `IntelligencePanel.tsx:142-145` | `.banner.banner-danger` on draft error |
| `StartupGate.tsx` | rewritten in Phase 1: named diagnostic code + guidance + log path |

`OverviewPage`, `TasksPage`, `DeadlinesPage` and `SettingsPage` have **no error branch at
all** — a failed query renders the empty state, so a connection failure is
indistinguishable from an empty mailbox. This is the most serious state defect found.

## 12. Responsive behaviour

One window media query: `@media (max-width: 1100px)` (`globals.css:2163`).
Four container queries: `mail-pane` at 520 px and 360 px; `mail-workspace` at 900 px and
600 px.

Using container queries for a resizable pane rather than window width is **correct** and
is preserved. `minWidth` is 900 px and `minHeight` 650 px in `tauri.conf.json`.

## 13. Accessibility behaviour

Counted across production `*.tsx`:

| | Count |
| --- | --- |
| `aria-hidden` | 74 |
| `aria-label` | 44 |
| `aria-busy` / `aria-pressed` / `aria-selected` | 5 / 5 / 3 |
| `aria-live` | 2 |
| `aria-current` | 1 |
| `role` | 22 |
| `tabIndex` | 2 |
| **`aria-describedby` / `aria-labelledby` / `aria-expanded` / `aria-controls`** | **0** |
| **`.sr-only` / skip link** | **0** |

Genuinely good: the category tablists implement the APG pattern with roving tabindex and
Arrow/Home/End (`CategoryTabs.tsx:31-58, 78`); `SourceEmailPreview` has a real focus trap
*and* focus restore (`:47-91`); focus-visible styling covers buttons, rows, inputs and
tabs (`globals.css:2550-2565`).

Gaps: no skip link; the default Mail view has **no `<h1>`** (only the reader's `<h2>`);
no focus movement on page change or message selection; `ThemeToggle` is a `radiogroup`
with no arrow-key handling and no roving tabindex; AI state changes are not announced;
`MailWorkspace.tsx:421` puts `aria-label` on a bare `<svg>` with no `role="img"`.

## 14. Virtualization

Present and correct in two places:

- `MessageList.tsx:22-25` — `useVirtualizer`, `estimateSize: () => 96`, `overscan: 8`,
  `measureElement` per row (`:60-71`), absolute positioning inside a sized container
- `TasksPage.tsx:61-64` — same pattern, `estimateSize: () => 60`

**Preserved. Not replaced with `.map()`.** Note the `estimateSize` values are coupled to
row height: changing row padding without updating `96` will cause scroll jitter.

## 15. Keyboard interactions

Exactly four places implement keyboard behaviour:

| Location | Keys |
| --- | --- |
| `WorkspaceHeader.tsx:30-43` | `Ctrl/Cmd+K` focus search, `Escape` blur (document-level) |
| `CategoryTabs.tsx:31-58` | Arrow/Home/End, roving tabindex |
| `MessageRow.tsx:47-53` | `Enter`/`Space` activate the `role="button"` row |
| `SourceEmailPreview.tsx:63-91` | `Escape` close, Tab/Shift+Tab trap |

**No keyboard shortcut exists for navigation.** The rail is six independently-tabbable
buttons with no arrow-key group behaviour and no `Ctrl+1..6`. Moving between Overview,
Tasks and Deadlines requires tabbing from the top of the document each time.

## 16. Reusable primitives

| Primitive | Location | State |
| --- | --- | --- |
| Button | `.btn` + `--primary`/`--surface`/`--danger`/`--sm`/`--block`/`--ghost` | CSS only, no component |
| Icon button | `.icon-btn`, `.filter-icon-btn` | CSS only |
| Badge | `.badge` + 6 variants | CSS only |
| Empty state | `.empty-state` | CSS only |
| Skeleton | `.skeleton`, `.skeleton-row` | CSS only |
| Banner | `.banner`, `.banner-danger` | CSS only |
| Dialog | `SourceEmailPreview` | **one implementation, inlined** |
| Progress | `AnalysisProgress` | component |
| Toggle group | `ThemeToggle` | component |

`.btn` appears in 9 files. There is **no** Button, Field, Dialog, Tooltip or Toast
component — every surface reimplements button markup, and the only dialog is inlined in
`SourceEmailPreview` with a hand-written focus trap. A second dialog would have to
duplicate that trap.

## 17. Components to preserve

| Component | Why |
| --- | --- |
| `mail/layoutStore.ts` | validated, versioned, persisted layout. Correct. |
| `MessageList` + `MessageRow` virtualization | correct pattern, real measurement |
| `CategoryTabs` | reference-quality APG tablist |
| `SourceEmailPreview` focus trap + restore | correct, tested |
| `lib/urlSecurity.ts` | protocol allow-list, 11 tests |
| `search/searchParser.ts` | 33 tests, full operator grammar |
| `theme/*` | pre-paint application, no flash, tested |
| `tokens.css` / `themes.css` | complete, dual-theme, measured |
| `LinkifiedBody` | allow-listed external navigation |
| `api/client.ts` | single base-URL + token authority |

## 18. Components to refactor

Not replaced — restructured to use shared primitives and real tokens.

| Component | Reason |
| --- | --- |
| `MailWorkspace.tsx` | 629 lines, 6 inline sub-components, 34 class names, 31 inline `style` objects across the codebase. Correct behaviour, wrong structure. |
| `IntelligencePanel.tsx` | Always renders a Priority section even with no data; no CONTEXT section; section order does not match the reading order of an email. |
| `MessageRow.tsx` | Up to 7 badges competing in one row; unread indicator is invisible at rest (§20). |
| `WorkspaceHeader.tsx` | Search is a bare input with an icon; no filter scope, no result count, no clear affordance. |
| `IconRail.tsx` | Icon-only with CSS tooltips; exposes none of the ten product capabilities. |
| `OverviewPage.tsx` | 32 class names, 4 metric cards + 2 column panels + accent wash — the "AI dashboard" pattern. |
| `AccountsPage.tsx` | OAuth via `window.open` popup; `message` listener does not verify `event.origin`; no `aria-label` on any of its 4 buttons. |
| `SettingsPage.tsx` | Second, independent copy of the 7-entry AI label map. |

## 19. Components that genuinely need replacement

| Item | Reason for replacement rather than refactor |
| --- | --- |
| `.message-row:hover { transform: translateX(3px) }` (`globals.css`) | Every hover reflows a virtualized row. Causes jitter, breaks scan rhythm, and moves the text the user is aiming at. Cannot be fixed by refactoring the component; the rule must go. |
| Unread affordance | `.message-row.unread::before` is `opacity: 0` and only becomes visible on `:hover` or `.selected`. **An unread row is visually identical to a read row at rest.** The dedicated indicator is dead code. |
| Error-less pages | Overview, Tasks, Deadlines and Settings conflate "failed" with "empty". Needs a new state branch, not a restyle. |
| Missing query/error primitives | No shared `Button`, `Field`, `Dialog`, `EmptyState`, `ErrorState`, `Tooltip` or `Toast`. Nine copies of button markup; one inlined dialog. |
| Ambient orb layer | `.ambient-layer` renders 4 blurred orbs (`App.tsx:119-123`) drifting at 110–140 s, with six `glass-*` `backdrop-filter` surfaces over them. Continuous full-viewport blur behind a reading application. |
| AI status colour coupling | Status is encoded by colour on small dots; needs an icon+label rule so colour is never the only channel. |

## 20. Concrete defects found

| # | Defect | Evidence | Severity |
| --- | --- | --- | --- |
| D1 | Unread rows indistinguishable from read at rest | `.message-row.unread::before { opacity: 0 }`, shown only on hover/selected | High |
| D2 | Hover shifts the row 3 px | `.message-row:hover { transform: translateX(3px) }` | High |
| D3 | 7 colour tokens fail WCAG AA | measured, §7 | High |
| D4 | 4 pages have no error state | Overview/Tasks/Deadlines/Settings | High |
| D5 | No `h1` on the default view | `App.tsx:145-172` renders no heading | High |
| D6 | No skip link, 0 `aria-describedby`/`aria-expanded`/`aria-controls` | counted, §13 | High |
| D7 | No keyboard navigation between pages | `IconRail` has no `onKeyDown` | Medium |
| D8 | `ThemeToggle` radiogroup with no arrow keys | `ThemeToggle.tsx:15-30` | Medium |
| D9 | 4 ambient orbs + 6 glass surfaces, continuous blur | `App.tsx:119-123`, `surfaces.css` | Medium |
| D10 | 2 broken token references | `styles.css:7,9` → undefined `--bg-elevated` | Medium |
| D11 | 4 empty states with no action | §10 | Medium |
| D12 | 31 inline `style` objects; skeleton sizes not tokens | counted | Medium |
| D13 | AI label map duplicated 3× | `WorkspaceHeader.tsx:4-12`, `SettingsPage.tsx:6-14`, `AnalysisProgress.tsx:85-115` | Medium |
| D14 | No Button/Dialog/Field/Toast primitive | §16 | Medium |
| D15 | `.search-shortcut` hardcodes `Ctrl K` | `WorkspaceHeader.tsx:67` | Low |
| D16 | `aria-label` on a bare `<svg>` | `MailWorkspace.tsx:421` | Low |
| D17 | Non-standard `font-weight: 650` | `.message-sender` | Low |
| D18 | `estimateSize: 96` coupled to row height | `MessageList.tsx:23` | Low |

## 21. Information hierarchy problems

1. **Two navigation surfaces, never reconciled.** The rail shows pages; the mail pane
   shows Inbox/All Mail, categories, kinds and four filters. A user in Tasks cannot see
   which mail filter is active, and a user in the rail cannot see that a filter is
   narrowing the list.
2. **The intelligence panel outranks the email it describes.** The reader's `<h2>` subject
   sits above the body, but the panel is a full-height peer pane with a bold title and a
   prominent `Generate Draft` primary button. Draft generation is more visually dominant
   than reading the message.
3. **Priority is always shown.** `IntelligencePanel.tsx:71-87` renders the Priority
   section unconditionally, even when the model reported nothing. Three of six sections
   are conditional; Priority should be the same.
4. **Overview is a dashboard.** Four metric cards, two column panels, and an accent-wash
   briefing panel — 32 class names for one screen. The greeting is an `<h1>` on a time of
   day, which pushes real content below the fold.
5. **The message row has no resting priority signal.** Importance is a badge in the
   bottom row, competing with up to six other badges.

## 22. Summary

The system is **structurally sound and visually unfinished**. The bones are good: a real
grid shell, a complete dual-theme token set, correct container-query responsiveness,
correct virtualization, a reference-quality tablist, a tested dialog with focus
management, and a system font stack with zero webfont cost.

What is missing is restraint and a component layer. The interface decorates
(`ambient-layer`, six glass surfaces, a 3 px hover shift, seven competing badges) and
lacks the primitives that would let it stop doing that. The most serious functional
defects are that unread is invisible, four pages cannot show an error, and seven colour
tokens fail AA.

The plan in `docs/UI-DESIGN-SPEC.md` addresses these without replacing working
architecture.
