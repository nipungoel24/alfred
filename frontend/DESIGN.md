# Alfred Design System

## Design Identity

Alfred is a **premium dark desktop application** for executive inbox management. The design language draws from Gmail's information architecture while maintaining a distinct, restrained aesthetic.

### Core Principles

1. **Gmail-inspired information architecture** — NOT Gmail branding
2. **Premium dark desktop application** — NOT a web app or mobile clone
3. **Restrained glassmorphism** — Subtle transparency, not blur-everything
4. **Fast, dense, calm, professional** — Productivity-first design
5. **Local-first** — No marketing-page aesthetic, no neon dashboard

### Anti-Patterns (Do NOT use)

- Cyberpunk aesthetic
- Neon dashboard elements
- Giant gradients
- Card soup (every surface wrapped in Card)
- Marketing-page aesthetic
- Animated email rows while scrolling
- Constant glowing/pulsing
- Bouncing navigation

## Visual Language

### Color System

**Dark Theme (Primary)**
- Background: Deep navy/charcoal (`#080a12`)
- Surface: Semi-transparent dark (`rgba(20, 24, 38, 0.92)`)
- Text: Light gray hierarchy (`#eaecf5`, `#b0b5cc`, `#8891a5`)
- Accent: Violet (`#7c6cf2`) for primary actions
- Success: Mint (`#5bd6a0`)
- Error: Coral (`#f28b82`)

**Semantic Tokens**
```css
--background: 222 47% 6%;
--foreground: 225 25% 92%;
--card: 222 40% 12%;
--card-foreground: 225 25% 92%;
--primary: 250 56% 65%;
--primary-foreground: 0 0% 100%;
--secondary: 222 30% 16%;
--muted: 222 30% 16%;
--muted-foreground: 225 15% 55%;
--accent: 222 30% 16%;
--border: 222 25% 18%;
--input: 222 25% 18%;
--ring: 250 56% 65%;
--destructive: 0 72% 71%;
```

### Typography

**Font Stack**
```css
--font-sans: 'Segoe UI Variable Text', 'Segoe UI', -apple-system,
             BlinkMacSystemFont, 'Inter', system-ui, sans-serif;
--font-mono: 'Cascadia Code', 'Consolas', 'SF Mono', monospace;
```

**Type Scale**
- xs: 11.5px (labels, captions)
- sm: 13px (secondary text)
- base: 14px (body)
- md: 15.5px (emphasis)
- lg: 17.5px (subheadings)
- xl: 20px (headings)
- 2xl: 23px (section titles)
- 3xl: 27px (page titles)

### Spacing

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
```

### Motion

**Budget (transform/opacity only)**
```css
--motion-micro:   110ms cubic-bezier(0.2, 0, 0, 1);
--motion-hover:   150ms cubic-bezier(0.2, 0, 0, 1);
--motion-pane:    220ms cubic-bezier(0.22, 1, 0.36, 1);
--motion-reveal:  300ms cubic-bezier(0.22, 1, 0.36, 1);
--motion-spring:  420ms cubic-bezier(0.22, 1, 0.36, 1);
```

**Principles**
- Press feedback: 100-160ms
- Tooltips/popovers: 125-200ms
- Dropdowns/selects: 150-250ms
- Drawers/dialogs: 200-400ms
- Respect `prefers-reduced-motion`

### Radii

```css
--radius-xs: 2px;
--radius-sm: 4px;
--radius-md: 6px;
--radius-lg: 10px;
--radius-xl: 14px;
--radius-full: 9999px;
```

### Glass Effects

**Usage**
- Sidebar
- Top bar
- Command palette
- Floating toolbar
- Intelligence panel
- Dialog/popover

**NOT on**
- Email rows (expensive, noisy)
- Dense data surfaces (stay flat)

**CSS**
```css
--blur-soft: 14px;
--blur-strong: 22px;
```

## Layout

### Application Shell

```
┌─────────────────────────────────────────────────────────────┐
│ Alfred   Search mail, people, tasks...       AI • Account │
├───────────────┬─────────────────────────────────────────────┤
│ Sidebar       │ Workspace                                   │
│               │                                             │
│ Overview      │                                             │
│ Inbox         │                                             │
│ Important     │                                             │
│ Needs Reply   │                                             │
│ Later         │                                             │
│ Tasks         │                                             │
│ Deadlines     │                                             │
│ Accounts      │                                             │
│ Settings      │                                             │
│               │                                             │
│ Local AI      │                                             │
└───────────────┴─────────────────────────────────────────────┘
```

### Sidebar (IconRail)

- Width: 56px (collapsed)
- Expanded: 200px (optional)
- Groups: Overview, Mail, Organize, System
- Status indicators: AI, Gmail connection

### Workspace Header

- Height: 52px
- Global search (Ctrl+K)
- Account avatar
- AI status indicator

### Mail Workspace

- Three-pane layout: Category Tabs | Message List | Message Detail
- Virtualized message list
- Dense rows (not cards)
- Intelligence signals: HIGH, REPLY, TASK, DUE

## Components

### shadcn/ui Integration

**Foundation**
- Sidebar
- Button
- Input
- Command (Ctrl+K search)
- Tooltip
- Dropdown Menu
- Dialog
- Sheet
- Badge
- Avatar
- Skeleton
- Separator
- Tabs
- Scroll Area
- Popover
- Collapsible
- Sonner (toast notifications)

**NOT used**
- Card (except for truly card-like information)
- Every surface wrapped in Card

### Icon System

**Primary**: Lucide React (consistent stroke language)
**Brand**: theSVG (Gmail, Google provider icons)
**Stateful**: Morphicons (only for semantic state changes)

**Morphicons Usage**
- Sidebar menu ↔ close
- Expand ↔ collapse
- Play ↔ pause
- Eye ↔ eye-off
- Sync idle ↔ active

**NOT morphing**
- Every sidebar icon
- Continuous animation

## Pages

### Overview

**Goal**: What needs my attention?

**Structure**
- Greeting: Good morning/afternoon/evening
- Metrics: Important, Needs reply, Tasks, Deadlines
- Needs attention list
- Upcoming deadlines
- Concise Alfred briefing

**NOT**
- Statistics about statistics
- AI-meta language
- "The user has provided 52 emails..."

### Inbox

**Goal**: Dense Gmail-inspired message list

**Structure**
- Sender
- Subject
- Snippet
- Intelligence signals (1-2 max)
- Timestamp
- Unread stronger, read quieter

**NOT**
- Cards
- Blur on rows

### Email Detail

**Goal**: Original email + Alfred Intelligence

**Structure**
- Primary: Original email
- Secondary: Alfred Intelligence panel
  - Summary
  - Priority
  - Why it matters
  - Needs reply
  - Actions
  - Deadline
  - Important details
  - Draft

**NOT**
- null, [], raw schema, raw JSON
- Empty sections

### Tasks

**Goal**: Productivity list

**Structure**
- Tabs: Open, Completed, All
- Groups: Today, This week, Later
- Rows: Checkbox, task, source, deadline, priority

### Deadlines

**Goal**: Timeline/grouped dates

**Structure**
- Today, Tomorrow, This week, Later
- Human-readable timestamps
- NOT raw ISO date strings

### Accounts

**Goal**: Professional provider management

**Structure**
- Gmail card with brand icon
- Account address
- Connected state
- Last sync
- Sync now button
- Disconnect option

### Settings

**Goal**: Clean configuration groups

**Structure**
- LOCAL AI: Model, Status
- PRIVACY: Local AI processing, local storage
- APPLICATION: Theme, data location, version/build identity

## Accessibility

- Semantic HTML
- Accessible shadcn primitives
- Keyboard focus management
- aria-label on interactive elements
- Correct dialog behavior
- Correct tooltips
- Sufficient contrast
- Ctrl+K: Global search
- Esc: Dismiss modal/panel
- Respect reduced-motion

## Performance

- React Query for data fetching
- SSE for real-time updates
- Virtualized message lists
- Cached UI state
- No animation on virtualization measurements
- No backdrop-filter on thousands of items

## Responsive Targets

- 1280×720
- 1366×768
- 1440×900
- 1920×1080

Windows desktop first. NOT phone layouts.

## Accepted Changes — Mail Workspace Productization (2026-09)

### Mail-pane container queries (not window queries)

`.mail-pane` is the CSS inline-size container (`container-type: inline-size;
container-name: mail-pane`). All mail-pane responsiveness keys off
`@container mail-pane (...)` so dragging the mail/reader separator changes
the mail layout — window size alone does not.

- Mail pane ≤ 520px: the filter field drops to its own full-width row
  (`order: 10; flex-basis: 100%`), the spacer is hidden, the Sync button
  collapses to icon-only (keeps `aria-label`, `title`, focus ring).
- Mail pane ≤ 360px: filter buttons compress; labels stay readable
  (no cryptic abbreviations).
- Category tabs wrap (`flex-wrap: wrap; overflow: hidden`) — never clipped,
  never invisible horizontal scroll.
- Intelligence panel: `react-resizable-panels` Group/Panel/Separator with
  `minSize`/`maxSize`, `collapsible` + `collapsedSize={0}`; layout persisted
  to `localStorage` (`alfred-pane-layout`); broken layouts are rejected on
  read (type check) so a saved layout can never brick the workspace.

### Mail toolbar states

- Wide: `All | Important | Reply | Later … [Filter box growing] [Sync]`
- Medium: same, Sync becomes icon-only via `.sync-label` hiding.
- Narrow: search is a full-width second row; primary filters stay visible.

Rules: `min-width: 0` on all flex children, `flex-wrap`, no `overflow-x:
auto` on toolbars, nothing bleeds into the reader pane.

### AI state machine (user-visible labels)

`initializing → ready | ollama_not_running | model_missing |
temporarily_unavailable | recovering | error`. Never Python exception names.
Rail/header chips and Settings show the same labels. The analysis status
pill is compact (bottom-left, max 560px, not full-width):

- `ready + pending>0`: "Analyzing N messages · Local AI ready" (spinner)
- offline states: "Local AI offline · N analyses queued" + Retry button
- `model_missing`: "qwen3:4b needs to be installed · N queued"
- No spinner when nothing can execute.

### Structured search

`searchParser.parseSearchQuery()` → typed `SearchFilters` → POST
`/api/emails/search` → parameterized SQL before LIMIT/OFFSET; free text
over FTS5 + BM25. Only advertised operators: `from: subject: is:unread
is:read is:important is:reply after: before: category: in:` plus free text.
`has:attachment` is NOT supported (attachments aren't stored) and degrades
to free text. Active filters render as removable chips + "Clear all".

### Build identity

- Desktop: compile-time `ALFRED_GIT_COMMIT` (build.rs) → desktop.log
  `build=` line; passed to the sidecar as `ALFRED_BACKEND_BUILD`.
- Backend: `/health.build` + Settings → About.
- Frontend: `__ALFRED_BUILD__` (vite define, git short SHA) → Settings →
  About. Running-build staleness is checkable in-app.

### External links

`LinkifiedBody` renders plain React text + linkify-it 5.x matches.
`isAllowedExternalUrl()` allows exactly `https http mailto tel`. In Tauri,
`@tauri-apps/plugin-opener openUrl()` is the only opener (a rejected
permission stays rejected — no shell fallback). `window.open` only outside
Tauri.
