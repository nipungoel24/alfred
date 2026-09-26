# Alfred — UI Design Specification

Status: active
Date: 2026-09-26, Phase 1
Supersedes: `frontend/DESIGN.md` (stale: describes an 8-item sidebar and 16 shadcn
components that do not exist)
Companion: `docs/UI-AUDIT.md` (what exists), `docs/Design.md` (brand and rationale),
`docs/decisions/ADR-005` (accent decision)

This is the source of truth for Alfred's interface. Where it disagrees with
`frontend/DESIGN.md`, this document wins. Where it disagrees with the code, the code is
the defect.

---

## 0. Product character

Alfred is a desktop instrument for reading one's own mail. It should feel like a
well-made native Windows application that happens to have intelligence attached — not a
web page, not a dashboard, not a demo.

Three commitments:

1. **Ink on paper.** Reading is the primary act. Typography, measure and leading outrank
   decoration everywhere.
2. **Density with air.** A serious mail client shows a lot per screen. Density comes
   from tight leading and small metadata, not from removing whitespace between
   elements.
3. **Restraint is a feature.** Alfred's intelligence is genuinely useful. It does not need
   a gradient, an orb field, or a card to announce itself. Confidence comes from
   precision: real states, real data, no invented content.

Explicitly rejected: gradient text, glassmorphism over moving backgrounds, oversized
hero sections, pill-per-option, icon-as-decoration, fake metrics, fake avatars,
placeholder AI copy, and animation that exists to impress.

---

## 1. Typography

### Family

```
--font-sans: 'Segoe UI Variable Text', 'Segoe UI', system-ui, -apple-system, sans-serif;
--font-mono: 'Cascadia Code', 'Consolas', ui-monospace, monospace;
```

Windows-native, variable-weight, **zero webfont bytes**. Do not add a webfont.

### Scale

One scale. Sizes are from the existing `tokens.css` and are kept — the scale was already
correct.

| Token | Size | Line height | Role |
| --- | --- | --- | --- |
| `--text-2xs` | 10.5px | 1.4 | legal/diagnostic mono only |
| `--text-xs` | 11.5px | 1.45 | metadata, counts, timestamps, badges |
| `--text-sm` | 13px | 1.5 | **secondary body**: subjects, list rows, table cells |
| `--text-base` | 14px | 1.55 | **primary body**: message body, panel prose |
| `--text-md` | 15.5px | 1.6 | emphasised body, reader lead paragraph |
| `--text-lg` | 17.5px | 1.35 | pane and card titles |
| `--text-xl` | 20px | 1.3 | page titles |
| `--text-2xl` | 23px | 1.3 | reader subject |
| `--text-3xl` | 27px | 1.25 | reserved: briefing headline only |

`--leading-reader 1.66` is used for the message body and source preview. Long-form mail
needs more air than UI chrome; that is what the token is for.

### Weights

Four steps only. No `650`.

| Token | Value | Use |
| --- | --- | --- |
| `--weight-regular` | 400 | body, metadata |
| `--weight-medium` | 500 | secondary emphasis, read-row sender |
| `--weight-semibold` | 600 | subjects, labels, active nav |
| `--weight-bold` | 700 | page titles, unread sender, selected sender |

**Unread must not rely on weight alone** — see §11.

### Letter spacing

| Role | Tracking |
| --- | --- |
| Page/reader titles | `-0.015em` |
| Subjects, senders | `-0.005em` |
| All-caps section labels | `0.04em` |
| Body, metadata | `0` |
| Diagnostic codes (mono) | `0.01em` |

### Measure

Reading surfaces cap at **68ch**. Narrower panes cap at `100%`. Never let a body line
exceed ~80 characters.

---

## 2. Spacing

A single 4 px scale. No one-off values.

| Token | Value |
| --- | --- |
| `--space-0` | 0 |
| `--space-1` | 4px |
| `--space-2` | 8px |
| `--space-3` | 12px |
| `--space-4` | 16px |
| `--space-5` | 20px |
| `--space-6` | 24px |
| `--space-8` | 32px |
| `--space-10` | 40px |
| `--space-12` | 48px |

Rules:
- **Component internals** use `--space-1` … `--space-4` only.
- **Panel padding** is `--space-4` (16px) for panes, `--space-5` for page containers.
- **Section separation** inside a panel is `--space-6`.
- Page gutters are `--space-8` at ≥1200px, `--space-5` below.
- 6px, 10px, 14px, 18px, 22px, 28px, 36px, 44px do not exist. If a design needs one,
  the scale is wrong, not the design.

**No inline `style={{ padding: N }}` in components.** All 31 current occurrences are
migrated to tokens or classes.

---

## 3. Colour

Semantic tokens only. Components never reference a raw hex.

### 3.1 Surfaces

| Token | Light | Dark | Use |
| --- | --- | --- | --- |
| `--bg-app` | `#f2f3f8` | `#0b0d13` | window background behind all panels |
| `--bg-panel` | `#ffffff` | `#131620` | rail, header, pane background |
| `--bg-elevated` | `#ffffff` | `#1a1f2b` | menus, dialogs, popovers — **now defined** |
| `--bg-reader` | `#fdfdfc` | `#151a24` | the reading surface, deliberately distinct |
| `--bg-sunken` | `rgba(28,32,41,.045)` | `rgba(0,0,0,.28)` | wells, inset areas, skeletons |
| `--bg-row-hover` | `rgba(28,32,41,.05)` | `rgba(255,255,255,.045)` | row/list hover |
| `--bg-row-active` | accent @ 10% | accent @ 16% | keyboard-focused row |
| `--bg-row-selected` | accent @ 8% | accent @ 14% | the selected row |

**Alpha-tinted row states only.** No opaque row colours — they must sit over any surface.

### 3.2 Text

| Token | Light | Dark | Contrast (worst surface) |
| --- | --- | --- | --- |
| `--text-primary` | `#1c2029` | `#eef0f5` | 14.71 |
| `--text-secondary` | `#444a5e` | `#b3bacb` | 7.94 |
| `--text-muted` | `#646c80` | `#8b95ad` | 4.74 |
| `--text-faint` | `#7d8599` | `#75809c` | **decoration only** |
| `--text-inverse` | `#ffffff` | `#0b0d13` | on accent fills |

`--text-muted` is the new default for metadata. `--text-faint` is **decoration only**:
dividers, placeholder glyphs, disabled strokes. Any text uses `--text-secondary` or
`--text-muted`. This resolves the unfixable contrast of a "faint" text colour by
restricting what it may be used for.

### 3.3 Accent

Per ADR-005: teal.

| Token | Light | Dark |
| --- | --- | --- |
| `--accent` | `#0b6b6b` | `#3fb8b0` |
| `--accent-hover` | `#095a5a` | `#5ccbc3` |
| `--accent-active` | `#074949` | `#7fd8d1` |
| `--accent-text` | `#0b6b6b` | `#3fb8b0` |
| `--accent-soft` | `rgba(11,107,107,.10)` | `rgba(63,184,176,.14)` |
| `--border-focus` | `#0b6b6b` | `#3fb8b0` |

Worst-case contrast 5.69 light / 7.21 dark, against 4.5 required. Headroom +1.19.

**Accent means: selected, focused, unread, primary action. Nothing else.** It is never
decoration, never a background wash, never a status colour. This rule is what resolves
teal's 20° hue proximity to success-green (§3.5).

### 3.4 Semantic

| Token | Light | Dark | Worst contrast |
| --- | --- | --- | --- |
| `--success` | `#0f7d59` | `#3ecf8e` | 4.62 |
| `--warning` | `#8a5f0e` | `#e8b44f` | 5.09 |
| `--danger` | `#c53f3f` | `#ef7d7d` | 4.56 |
| `--info` | `#1f6fc4` | `#5fa8f5` | 4.59 |

Each has a `-soft` tint at 10% for backgrounds. Semantic colours are for state only —
connected, degraded, failed, informational. Never decorative.

### 3.5 The colour rule

Because teal (hue 180°) sits only 20° from success-green (hue 160°), the two must never
be the sole distinguishing channel for adjacent elements. Enforced as:

1. **Status is never colour alone.** Every status indicator carries an icon *and* an
   accessible label. A coloured dot by itself is not permitted.
2. **Accent is never a status.** If something is coloured with `--accent`, it means
   selection or focus. Connection and health use §3.4.
3. **Unread carries three signals**: a left accent bar, `--weight-semibold` sender, and
   `aria-label`/`.sr-only` text. Remove any one and two remain.

### 3.6 Priority ramp

Separate from semantics; a badge must never borrow a semantic hue for priority.

| Level | `--priority-*-bg` | `--priority-*-fg` |
| --- | --- | --- |
| urgent | `rgba(197,63,63,.12)` | `#a82f2f` |
| high | `rgba(138,95,14,.14)` | `#6f4c0b` |
| medium | `rgba(31,111,196,.12)` | `#1a5a9e` |
| low | `rgba(90,100,130,.10)` | `#5a6280` |

---

## 4. Radius

| Token | Value | Applied to |
| --- | --- | --- |
| `--radius-xs` | 2px | badges, inline chips, focus-ring inner edge |
| `--radius-sm` | 4px | inputs, small buttons, list controls |
| `--radius-md` | 6px | panels, cards, list rows (interactive) |
| `--radius-lg` | 8px | dialogs, popovers, the app icon tile |
| `--radius-full` | 9999px | **only** genuinely circular: status dot, avatar |

Rules:
- Most of Alfred's surface area sits at `--radius-sm` or `--radius-md`. It is a dense
  tool.
- `--radius-lg` is for overlays only. A panel is not a card and does not get a large
  radius.
- **Not every element gets rounded corners.** Dividers, table rows, list rows inside a
  bordered container, and full-bleed sections are square. Borders create the structure;
  radius is reserved for interactive surfaces and overlays.
- A pill shape is permitted for exactly three things: a status dot, a badge whose content
  is a count, and a segmented-control track. Nothing else.

---

## 5. Borders

Four steps. Hierarchy comes from borders, not shadows.

| Token | Use |
| --- | --- |
| `--border-subtle` | row dividers, internal separation |
| `--border-default` | panel edges, input outlines, control borders |
| `--border-hover` | interactive edge on hover |
| `--border-focus` | focus ring, 2px |

Rules:
- A 1 px `--border-subtle` divider between list rows is the primary separation device.
  Do not add a shadow to a row.
- Never stack two borders on one edge.
- Selected state uses `inset 3px 0 0 var(--accent)` on the left edge, not a full outline.

---

## 6. Shadows

Three levels. Elevation only — never glow, never decoration.

| Token | Use |
| --- | --- |
| `--shadow-1` | resting raised surface: dialog, popover, the app icon tile |
| `--shadow-2` | overlay above a dialog: tooltip, context menu |
| `--shadow-3` | modal: only `SourceEmailPreview` |

Rules:
- List rows, panes, buttons and inputs get **no shadow**. They get a border.
- The reader surface gets a single `--shadow-1` at most, to separate it from the pane.
- No coloured shadow. `--shadow-accent` is removed.

---

## 7. Motion

### Duration

| Token | Value | Use |
| --- | --- | --- |
| `--motion-micro` | 110ms | hover, focus, colour and opacity changes |
| `--motion-hover` | 150ms | transform on hover |
| `--motion-pane` | 220ms | pane resize settle, disclosure |
| `--motion-reveal` | 300ms | list/panel entrance |

### Easing

- Standard: `cubic-bezier(0.2, 0, 0, 1)` — micro and hover
- Decelerate: `cubic-bezier(0.22, 1, 0.36, 1)` — pane and reveal
- **No bounce, no spring, no overshoot** anywhere.

### May animate

- Hover/focus colour, opacity, `background-color`
- Selected-state left bar: `opacity` and `transform: scaleY()`
- Pane disclosure: `width`/`opacity` on collapse
- Skeleton shimmer
- Progress bar width for real progress
- List entrance: opacity + 4px rise, staggered ≤45ms, ≤6 items

### Must never animate

- **Layout-affecting hover.** No `translateX` on a list row, no `scale` on a row, no
  width change on hover. A moving target cannot be aimed at.
- The ambient orb layer — **removed entirely**.
- Anything over 300ms except pane resize.
- Anything that delays interaction. Feedback must be immediate.
- Scroll-linked effects. There are none.
- Content that the user is reading.

### Reduced motion

Two layers, both required:
1. All `--motion-*` tokens resolve to `0ms` inside `prefers-reduced-motion: reduce`.
2. A global `!important` override zeroes `animation-duration` and `transition-duration`.

Any JS-driven motion must also check `matchMedia('(prefers-reduced-motion: reduce)')`.

---

## 8. Icons

**One library: `lucide-react`.** Already used across 30+ components with zero emoji and
no competing set. No new icon dependency.

Rules:
1. An icon appears only where it carries meaning: a nav destination, a state, a tool
   action, or a file/attachment type.
2. **Never decorative.** No icons scattered through body copy to break up text.
3. An icon-only control requires `aria-label`. `title` is a tooltip, not a name.
4. Size: 14px inline, 16px in controls, 18px in nav, 24px+ only in empty states.
5. `strokeWidth={2}` (1.75 in the rail) everywhere. No filled variants alongside stroked
   ones.
6. Status is icon + label, never icon + colour alone (§3.5).

`Morph Icons`, `TheSVG`, `shadcn/ui`, `ibelick/ui-skills` and `emilkowalski/skills` are
**reference material for judgement** — density, restraint, interaction craft. They are
not dependencies. Adding a second icon library is prohibited by `docs/Rules.md` §3.

### Brand marks

A separate concern, still placeholder at Gate 0. Required set: app icon, installer icon,
taskbar icon, splash mark, light and dark marks, monochrome mark, favicon, OG image.

---

## 9. Layout

### 9.1 Shell

```
grid-template-columns: var(--rail-width) 1fr;
grid-template-rows:    var(--header-height) 1fr;
grid-template-areas:   'rail header' 'rail content';
```

- `--rail-width: 232px` (was 56px — see §9.2)
- `--header-height: 52px`
- `overflow: hidden` on the shell; every region owns its own overflow

### 9.2 Sidebar

**The rail widens to 232 px and becomes the primary navigation.** Reason: the audit
found the product's ten capabilities split across two surfaces that never show each
other's state (§UI-AUDIT §21). A 56 px icon rail cannot carry labels, unread counts, or
filter state, so those live in the mail pane where they are invisible from other pages.

Structure, in the order a reader scans it:

```
MAIL
  Inbox                [count]
  All Mail             [count]
  Important            [count]
  Needs Reply          [count]
  Later                [count]
INTELLIGENCE
  Overview
  Tasks                [count]
  Deadlines            [count]
SYSTEM
  Accounts
  Settings
─────────────
  [account identity]
  [AI status: icon + label]
  [Gmail status: icon + label]
```

Rules:
- **No feature is removed.** All ten capabilities above already exist and work; this
  makes them discoverable from one place. Inbox/All Mail/Important/Needs Reply/Later
  drive the mail view; they are not deleted routes.
- Sections are `--text-2xs`, uppercase, `--text-muted`, `--space-4` top margin.
- Items are 32px tall, `--radius-sm`, 10px horizontal padding, icon 16px + label
  `--text-sm`.
- **Active**: `--accent-soft` background, `--accent` 2px left bar, label
  `--text-primary` `--weight-semibold`, `aria-current="page"`.
- **Hover**: `--bg-row-hover`, no transform.
- **Focus-visible**: the standard 2-layer ring.
- Counts are `--text-xs` `--text-muted`, `tabular-nums`, right-aligned. A zero count is
  shown as `0`, not hidden — a hidden count is ambiguous.
- Nav is one `role="navigation"` landmark with a single `aria-label`.
- **Arrow-key navigation** within the rail (Up/Down/Home/End) with roving tabindex, so
  the whole sidebar is one tab stop.
- Below 1100px window width the rail collapses to 56px icon-only, keeping
  `aria-label` on every item and `data-label` tooltips.

### 9.3 Header

One row, 52px:

```
[page title]  [ — subtitle — ]        [ search……………]  [sync]  [AI chip]  [account]
```

- **Search is a first-class control**, not a bare input: 320px min, `--radius-sm`,
  `--border-default`, leading search icon (decorative, `aria-hidden`), trailing clear
  button when non-empty, and a `Ctrl K` hint rendered from the platform.
- **The header search is global.** It searches the whole mailbox. When it is active the
  mail pane shows a scope banner naming the scope, and the sidebar dims its filters to
  make it clear the list is not filtered. This resolves the two-surface confusion.
- Sync button: icon + label, disabled while running (no click stacking), `aria-busy`.
- AI chip: icon + text label, never a bare dot.
- Account chip: initial in a circle + the connected address, with a tooltip.

### 9.4 Mail view

Three panes, unchanged in structure:

```
┌──────────────┬─────────────────────────┬──────────────────┐
│ List         │ Reader                  │ Alfred           │
│ 320–460px    │ flex, min 420px         │ 300–380px        │
│ -            │                         │ -                │
│ view switch  │ subject (h2)            │ SUMMARY          │
│ categories   │ from / to / date        │ WHY IT MATTERS   │
│ kind switch  │ ─────────────────       │ NEEDS REPLY      │
│ backfill     │ body                    │ TASKS            │
│ toolbar      │ attachments             │ DEADLINES        │
│ ─────────    │ ─────────────────       │ CONTEXT          │
│ virtualised  │ actions                 │                  │
│ rows         │                         │                  │
└──────────────┴─────────────────────────┴──────────────────┘
```

**Only the list pane is a container.** `.mail-pane` is `container-name: mail-pane`, so
list-pane rules respond to the list's own width. The reader and the intelligence pane
are **siblings** of the list pane, not descendants, so nothing inside either can be
reached from `@container mail-pane` — a rule written there matches nothing. Their
rules live in `@container mail-workspace`, because `.mail-workspace` is the container
that actually contains them. A container query is only as good as the ancestor it
names; check the DOM before trusting one.

### 9.5 Message row

Resting anatomy, in visual priority order:

```
│▌ Alice Nakamura                    14:32 │   ← accent bar if unread
│  Quarterly report — needs your sign-off    │   ← subject, semibold if unread
│  Hi — the numbers are in the attached...   │   ← 1 line snippet, muted
│  [Important] [Reply] [Category]      [⏱]  │   ← ≤2 badges + Later action
```

Rules:
- **Unread**: 3px `--accent` left bar (always visible, not hover-gated) **+**
  `--weight-semibold` sender **+** `.sr-only` "Unread". Three channels (§3.5).
- **Read**: no bar, `--weight-medium` sender, `--text-secondary`.
- **Selected**: `--bg-row-selected`, `inset 3px 0 0 var(--accent)`, sender
  `--weight-bold` `--text-primary`, `aria-selected="true"`.
- **Hover**: `--bg-row-hover` only. **No transform.** A row never moves.
- **Focus-visible**: `inset 0 0 0 2px var(--border-focus)`.
- **Badges: maximum two.** Priority outranks everything; then reply-needed; then
  category. Sent/Archived are implied by the All Mail kind filter, not shown per row.
- **Timestamp**: `--text-xs`, `--text-muted`, `tabular-nums`, right-aligned, never
  wraps. Relative for <7 days, absolute after.
- **Subject and snippet**: single line, `text-overflow: ellipsis`. Two lines maximum
  total for the snippet.
- **Row height**: 88px resting, and `estimateSize` in the virtualiser is updated to
  match. Height and virtualiser estimate are declared together, never independently.
- Row is a `role="option"` inside `role="listbox"`, `aria-selected`, keyboard
  Up/Down/Home/End, Enter/Space to open.

### 9.6 Reading pane

Priority order, and it is a strict order:

1. Subject — `--text-2xl`, `--weight-semibold`, the only large type in the pane
2. From — `--text-sm` name, `--text-xs` `--text-muted` address beneath it
3. To — recipients as their own labelled field, not folded into the From line
4. Date — a `<time>` element carrying the machine-readable timestamp
5. Body — `--text-base`, `--leading-reader`, 68ch measure, `overflow-wrap: anywhere`
6. Attachments — a bordered list, `--radius-sm`, size in `--text-xs`
7. Actions — Later, Copy, Intelligence — `--text-xs` icon buttons, right-aligned

**Message actions are placed after the message content so primary reading and
metadata remain visually dominant.** A control bar above the subject competes with
the one thing the pane exists for. Putting the actions last also means the subject,
the correspondent and the body own the top of the pane, uninterrupted, and the
controls arrive only once the reader has what they came for.

From / To / Date are three separate labelled fields in a
`max-content minmax(0, 1fr)` grid, not one flex row and not a single concatenated
line. A long sender name or a long recipient list then wraps inside its own cell
instead of pushing the timestamp off the pane.

**The reader is the default view of this pane.** Intelligence lives in its own pane to
the right, never above the body. A user reading a message must not have their reading
interrupted by a panel that is trying to summarise it.

### 9.7 Alfred intelligence

The differentiator. Restrained, honest, and never above the mail.

Section order and inclusion rules:

| Section | Shown when | Content |
| --- | --- | --- |
| **SUMMARY** | `analysis.summary` exists | 2–4 sentences, `--text-sm` |
| **WHY IT MATTERS** | `analysis.why` exists | one sentence, `--text-sm`, `--text-secondary` |
| **NEEDS REPLY** | `analysis.needs_reply` | why a reply is needed, plus Generate draft |
| **DEADLINES** | `deadlines.length > 0` | description + absolute date |
| **TASKS** | `action_items.length > 0` | description, deduped |
| **CONTEXT** | thread or account context exists | prior messages in thread, account, age |

**Every section is conditional.** The existing implementation renders Priority
unconditionally (`IntelligencePanel.tsx:71-87`); that is removed. A section with no data
is not rendered — not rendered as an empty box, not rendered as "—" (except the
explicit key/value rows where a value is genuinely informative).

Empty states, real ones:
- **Analysis pending**: a skeleton plus "Analysing this message…". Not a fake summary.
- **AI runtime offline**: an icon, "Local AI is offline", and a Retry action. States the
  consequence: "Your mailbox works. Summaries resume when Ollama is running."
- **Model missing**: "The local model isn't installed", with a link to Settings.
- **No analysis for this message**: "This message wasn't analysed." with the reason if
  known (deferred category, excluded from pipeline).

Copy rule: Alfred never says "AI analysis will appear here" as a placeholder. If analysis
is genuinely pending, it says so. If it will not arrive, it says why.

---

## 10. States

Every state is designed. No browser-default rendering anywhere.

| State | Treatment |
| --- | --- |
| **Loading** | Skeleton matching the real layout. `aria-busy`. Skeleton dimensions are tokens, not inline styles. |
| **Empty inbox** | Icon + "Inbox is empty" + the one action that fixes it (Sync now). |
| **Empty search** | Icon + "No messages match “{query}”" + Clear search. Never conflated with an empty inbox. |
| **Empty filter** | "No important messages" — names the active filter. |
| **Error (list/page)** | Icon + plain sentence + Retry + diagnostic code in mono. **Required on every page that queries.** |
| **Backend unavailable** | A shell-level banner, not a per-page error: "Alfred's local service isn't responding" + Retry. The startup gate covers launch; this covers a mid-session loss. |
| **Account disconnected** | The account row shows a Disconnected state with a Reconnect action; the list shows a connect prompt rather than an empty mailbox. |
| **Syncing** | Sync button disabled with `aria-busy` + spinner; a determinate progress line when known. Never a click-stacking bug. |
| **Selected** | §9.5. |
| **Unread** | §9.5. |
| **Disabled** | `opacity: .55`, `cursor: not-allowed`, and `aria-disabled` when not a real `<button disabled>`. |
| **AI unavailable** | §9.7. |
| **Focused** | 2-layer ring on every focusable. |
| **Reduced motion** | §7. |

---

## 11. Accessibility

Target: **WCAG 2.1 AA**. These are requirements, not aspirations.

1. **One `<h1>` per view.** The Mail view gains an `<h1>` (visually the subject, or a
   visually-hidden "Mail" when nothing is selected). The reader subject is `<h2>`.
2. **Skip to content** is the first tab stop in the document and moves focus to `<main>`.
3. **Landmarks**: one `banner` (header), one `navigation` (sidebar), one `main`, one
   `complementary` (intelligence), plus `search` on the search region.
4. **Sidebar is one tab stop** with arrow-key navigation and roving tabindex.
5. **Message list** is `role="listbox"` / `role="option"` with `aria-selected`,
   `aria-setsize`/`aria-posinset` from the virtualiser, and full arrow-key navigation.
6. **No colour-only state.** Unread = bar + weight + text. Status = icon + label.
   Priority = badge text + colour, never colour alone.
7. **`aria-describedby`** on every input that has help or error text.
   **`aria-expanded`** on every disclosure. **`aria-controls`** where a control governs a
   region.
8. **`.sr-only`** exists and is used for text a screen reader needs and a sighted user
   does not.
9. **Focus management**: moving pages moves focus to the new `<h1>`. Selecting a message
   moves focus to the reader heading. Opening a dialog focuses its close button and
   restores focus to the opener (already correct in `SourceEmailPreview`).
10. **Dialog semantics**: `role="dialog"`, `aria-modal`, labelled by its title, focus
    trapped, `Escape` closes, focus restored.
11. **Every interactive element is a real `<button>`, `<a>`, `<input>` or `<select>`.**
    `role="button"` on a `<div>` only where a row must be one target, and then it also
    carries `tabindex` and Enter/Space.
12. **Contrast**: §3. Every text token ≥4.5:1 against every surface it is used on.
13. **Reduced motion**: §7.
14. **Target size**: minimum 28×28px for any control; 32px for sidebar items.

---

## 12. Keyboard

| Keys | Action |
| --- | --- |
| `Ctrl/Cmd + K` | Focus global search |
| `Escape` | Blur search, or close the topmost dialog |
| `↑` `↓` | Move within the sidebar, or within the message list |
| `Home` `End` | First/last item in the focused list |
| `Enter` | Open the focused message, activate the focused control |
| `Space` | Toggle the focused row's selection |
| `←` `→` | Move between category tabs |
| `Ctrl + 1…6` | Jump to Overview / Mail / Tasks / Deadlines / Accounts / Settings |
| `Ctrl + R` | Sync now |
| `?` | Show the shortcut list |
| `Tab` | Every interactive element, in DOM order |

Every shortcut is discoverable in-product via a `?` overlay, and documented in
`docs/`. No destructive shortcut exists without confirmation.

Platform-correct modifier rendering: `Ctrl K` on Windows, `Cmd K` on macOS. Never
hardcoded.

---

## 13. Responsive behaviour

Alfred is a Windows desktop app with `minWidth: 900px` / `minHeight: 650px`. This is
graceful degradation at narrow window widths, **not** a responsive website.

| Window width | Behaviour |
| --- | --- |
| ≥1280px | Full three panes. Sidebar 232px. |
| 1100–1280px | Sidebar collapses to 56px icon rail. Three panes retained. |
| 900–1100px | Sidebar collapsed **and** the intelligence pane collapses to a toggle. Two panes. |

Rules:
- **The list + reader pair is never lost.** Below 900px is out of scope by `minWidth`.
- No horizontal overflow of the document at any width, in either theme.
- Long unbroken tokens, URLs and long subjects wrap or ellipsize — never widen a pane.
- Dialogs clamp to the viewport with `--space-5` margins on all sides.
- Container queries drive pane-internal responsiveness; window media queries drive
  chrome-level changes. Both are already in place and are preserved.

---

## 14. Component layer

New primitives, built on the existing token system. No new dependency. Each exists
because §UI-AUDIT §18/§19 found the behaviour duplicated or missing.

| Primitive | Replaces | Why |
| --- | --- | --- |
| `Button` | 9 copies of `.btn` markup | one focus/disabled/loading contract |
| `IconButton` | `.icon-btn`, `.filter-icon-btn` | guarantees `aria-label` |
| `Badge` | 6 ad-hoc variants | caps the badge count, owns priority ramp |
| `EmptyState` | 7 ad-hoc blocks | one layout, one action slot |
| `ErrorState` | **missing entirely** | §UI-AUDIT D4 |
| `Skeleton` | 31 inline `style` blocks | token-driven dimensions |
| `Dialog` | 1 inlined implementation | focus trap + restore guaranteed everywhere |
| `Field` | 4 bare inputs | label, description, error wiring |
| `Tooltip` | 4 CSS `::after` hacks | accessible, `aria-describedby` |
| `StatusIndicator` | bare dots | icon + label, never colour alone |
| `Tabs` | 3 hand-rolled tablists | one keyboard contract |
| `Section` | `.overview-section` etc. | label + action + body |

`StatusIndicator`, `Section` and the settings row/label pair are now implemented in
`src/components/ui/Settings.tsx`. The label/value pair is a single component because
Accounts and Settings both needed it and neither wanted a bespoke one; nothing else
was added speculatively.

Status wording for the local-AI state machine lives in exactly one place,
`src/lib/aiState.ts`, because it was previously restated with five different
vocabularies across the header, the rail, the intelligence panel, the progress bar and
Settings. The other four call sites still carry their own wording and are the obvious
next consumer of that module.

Rule: a primitive is added only when ≥2 call sites need it, or when its absence causes a
defect (ErrorState, Dialog). No speculative components.

---

## 15. What this spec removes, and why

| Removed | Reason |
| --- | --- |
| `.ambient-layer` and 4 ambient orbs | Decorative motion with no state meaning; continuous full-viewport blur behind a reading app. `docs/Rules.md` §2.1. |
| 6 `glass-*` `backdrop-filter` tokens | With nothing moving behind them, blur buys nothing and costs a compositing layer. Replaced by opaque `--bg-panel`. |
| `@import "tailwindcss"` + `@theme inline` | Zero utility classes exist. The preflight is overridden by `reset.css`. Two resets fight. |
| `components.json`, `src/lib/utils.ts` | Vestigial. `cn()` is imported by nothing. |
| `sharp`, `png-to-ico`, `class-variance-authority`, `clsx`, `tailwind-merge`, `tailwindcss`, `@tailwindcss/vite` | Unused. See ADR-004. |
| `.message-row:hover { translateX(3px) }` | A moving hover target. §7. |
| Hover-gated unread bar | Unread must be visible at rest. §9.5. |
| `--shadow-accent` | Coloured shadow. §6. |
| `--highlight-top` | A fake inset gloss on raised surfaces. §6 allows shadow for elevation only, never decoration. Its 18 call sites were left rendering **no shadow at all**, because the declaration was invalid at computed-value time. |
| `--reader-border` | Duplicated `--border-subtle`. A separate "reader border" would mean the same thing twice. The reader surface and the intelligence pane share `--bg-reader`, so they share one subtle edge. |
| `--radius-xl` | Not a step in the §4 scale, which is `xs`/`sm`/`md`/`lg`/`full`. Overlays take `--radius-lg`; a panel takes `--radius-md`, because a panel is not a card. |
| `--bg-panel-solid` | Duplicated `--bg-panel`. |
| `--ambient-*` tokens | Orb palette. |
| `Priority` section in the intelligence panel (unconditional) | Renders an empty section when there is nothing to say. §9.7. |
| 2 of 7 badges from a message row | Density and signal-to-noise. §9.5. |

**These four tokens were never defined.** Every one of them was referenced and never
created, so every declaration naming one was invalid and silently rendered as *no
style at all* rather than as a wrong style — which is why no DOM test noticed. They
are listed here as removals so they are not reintroduced. **A static test now fails
the build if any custom property is referenced without either a definition or an
explicit fallback** (`src/styles/styles.test.ts`).

---

## 16. Implementation order

| Step | Scope |
| --- | --- |
| UI-1 | Shell, tokens, spacing, typography, removal of the orb layer and Tailwind preflight |
| UI-2 | Sidebar: 232px, labels, counts, arrow-key nav, active/hover/focus |
| UI-3 | Header: first-class search, sync, AI chip, account |
| UI-4 | Message list: row anatomy, unread, selection, hover, no transform |
| UI-5 | Reading pane: hierarchy, measure, actions, attachments |
| UI-6 | Intelligence: conditional sections, real empty states |
| UI-7 | States: loading, empty, error, offline, disconnected |
| UI-8 | Accounts and Settings onto the shared primitives |
| UI-9 | Responsive: 1100px and 900px behaviour |
| UI-10 | Accessibility: landmarks, headings, skip link, focus, aria |
| UI-11 | Motion and polish |

Each step: typecheck → lint → test → inspect. No accumulating hundreds of visual changes
before testing.
