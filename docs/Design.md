# Alfred — Design System

Status: active
Baseline: Gate 0, 2026-09-26

Canonical location for Alfred's design system. `frontend/DESIGN.md` (440 lines) is
**superseded** by this document and is reconciled/removed in Phase 3; it currently
describes an 8-item sidebar that does not exist and 16 shadcn components that were never
generated.

All contrast figures below were measured, not estimated. The measurement script and its
output are recorded in `docs/Memory.md` §Evidence.

---

## 1. Brand identity

Alfred is a serious desktop instrument for reading one's own mail. It should look like
a tool that a professional trusts with their inbox, not like a landing page.

Three commitments:

1. **Ink on paper.** Alfred is a reading product. Text contrast and typographic rhythm
   outrank decoration. The reader surface is a warm off-white in light mode
   (`--bg-reader: #fdfdfc`) and a cool near-black in dark mode (`#151a24`) — a deliberate
   paper/ink metaphor that is already in the code and worth keeping.
2. **One accent, used sparingly.** Accent means "this is selected", "this is focused",
   "this is you". It is not decoration and it is not a background wash.
3. **Nothing moves unless it reports state.** Alfred's motion budget is spent on
   disclosure, pane transitions, and progress — never on ambience.

## 2. What must be removed, and why

| Current | Location | Problem |
| --- | --- | --- |
| 4 blurred drifting "ambient orbs" (violet, indigo, cyan, pink) at 110-140 s loops | `styles/surfaces.css`, rendered by `App.tsx` | Decorative motion with no state meaning. It is the clearest "AI-generated" signal in the product, it costs a full-screen `filter: blur(110px)` layer on every frame, and it fights the reading surface. **Remove.** |
| Violet accent `#6d5ae0` / `#8b7bf5` | `styles/themes.css` | The only chromatic identity in the product is in the purple band, which reads as template default rather than a chosen brand. See §3. |
| Six `glass-*` tokens with `backdrop-filter` | `styles/surfaces.css` | Real translucency over a moving background is fake glassmorphism. Once the orbs go, the glass has nothing to refract and becomes a flat tint with a filter cost. **Reduce to two surfaces** (`--bg-panel`, `--bg-panel-solid`). |
| `@import "tailwindcss"` with zero utility classes | `styles.css:1` | Injects a preflight that `reset.css` then overrides. Pure cost, pure confusion. **Remove** along with the four unused Tailwind-family dependencies and the vestigial `components.json`. See ADR-004. |

None of this is a redesign for its own sake. Each item is either decorative motion with
no state meaning, an unreviewed template default, or a dependency that does nothing.

## 3. Colour tokens

### 3.1 Measured failures at Gate 0

Contrast computed with the WCAG 2.1 relative-luminance formula. AA body text requires
**4.5:1**; non-text UI and large text require **3.0:1**.

| Token | Light value | on `#ffffff` | on `#f2f3f8` | Verdict |
| --- | --- | --- | --- | --- |
| `--text-primary` | `#1c2029` | 16.30 | 14.71 | pass |
| `--text-secondary` | `#444a5e` | 8.80 | 7.94 | pass |
| `--text-muted` | `#767e97` | **4.04** | **3.64** | **FAIL** |
| `--text-faint` | `#a0a7bd` | **2.40** | **2.16** | **FAIL** |
| `--success` | `#15936a` | **3.88** | **3.50** | **FAIL** |
| `--warning` | `#b07d1a` | **3.62** | **3.27** | **FAIL** |
| `--info` | `#2e7fd6` | **4.10** | **3.70** | **FAIL** |
| `--danger` | `#d04848` | **4.47** | **4.03** | **FAIL** |
| `--accent` | `#6d5ae0` | 5.01 | 4.52 | pass |

| Token | Dark value | on `#131620` | on `#151a24` | Verdict |
| --- | --- | --- | --- | --- |
| `--text-primary` | `#eef0f5` | 15.83 | — | pass |
| `--text-secondary` | `#b3bacb` | 9.29 | — | pass |
| `--text-muted` | `#7c86a0` | 4.96 | 4.79 | pass |
| `--text-faint` | `#525c76` | **2.71** | **2.61** | **FAIL** |
| `--accent` | `#8b7bf5` | 5.37 | 5.19 | pass |

**Seven tokens fail AA in light mode and one in dark mode.** These are not decorative
values: `--text-muted` carries counts, timestamps, and metadata; `--text-faint` carries
attachment labels and timestamps in the reader; the semantic colours carry priority and
status text. This is a release blocker, tracked as F9 in `docs/Memory.md`.

### 3.2 Target token values

Chosen as the first value in each family that clears 4.5:1 against **both** the panel
white and the app background in light mode, and both panel and reader in dark mode. The
smallest sufficient change is preferred over a larger one, to keep the visual shift
minimal and reviewable.

| Token | Current | Target | Measured | Change |
| --- | --- | --- | --- | --- |
| `--text-muted` (light) | `#767e97` | `#646c80` | 5.25 / 4.74 | darken |
| `--text-faint` (light) | `#a0a7bd` | `#7d8599` → **use only for non-text decoration**; for text use `--text-muted` | 3.69 / 3.33 | reserve |
| `--text-faint` (dark) | `#525c76` | `#75809c` | 4.58 / 4.42 | lighten |
| `--success` | `#15936a` | `#0f7d59` | 5.12 / 4.62 | darken |
| `--warning` | `#b07d1a` | `#8a5f0e` | 5.64 / 5.09 | darken |
| `--info` | `#2e7fd6` | `#1f6fc4` | 5.09 / 4.59 | darken |
| `--danger` | `#d04848` | `#c53f3f` | 5.05 / 4.56 | darken |

`--text-faint` cannot be made to pass 4.5:1 as a *light* grey that still reads as
"faint". The honest resolution is a semantic rule rather than a colour: **`--text-faint`
is for decoration only** (dividers, placeholder glyphs, disabled strokes). Any text
uses `--text-secondary` or `--text-muted`. Phase 3 audits every `.text-muted` and
faint-coloured usage against this rule.

Dark-mode semantic colours already pass and are unchanged.

### 3.3 The accent decision

The accent is the product's only chromatic identity, so this is a real decision and not
a preference. Recorded as ADR-005; it needs explicit sign-off because it is visible
everywhere.

Constraint set:

- Must clear 4.5:1 on `#ffffff`, `#f2f3f8`, and `#fdfdfc` (light)
- Must clear 4.5:1 on `#131620`, `#0b0d13`, and `#151a24` (dark)
- Must clear 3.0:1 against its own background for the focus ring
- Must be distinguishable from `--info` (blue), `--success` (green), and `--danger` (red)
- Must not be in the purple band

Recommendation: a **restrained teal**.

| Role | Value | Measured |
| --- | --- | --- |
| `--accent` light | `#0b6b6b` | 6.31 on white, 5.69 on app, 6.20 on reader |
| `--accent` dark | `#3fb8b0` | 7.47 on panel, 8.04 on app, 7.21 on reader |
| `--accent-text` light | `#0b6b6b` | 6.31 |
| `--accent-text` dark | `#3fb8b0` | 7.47 |

It clears AA with real headroom, is unambiguous against the semantic set, and reads as
an instrument rather than a gradient. Derived tokens (`--accent-hover`,
`--accent-active`, `--accent-soft`, `--shadow-accent`, `--border-focus`, `--unread-dot`,
and the four `*-soft` tints) are recomputed from these in Phase 3; each is re-measured,
not eyeballed.

**The alternative is to keep violet.** It passes AA today. It is rejected because a
single purple accent plus purple orbs is the most common visual signature of
AI-generated interfaces, and Alfred's credibility rests on looking considered. If the
owner prefers violet, that is a legitimate call — it needs one line in ADR-005 and the
orb removal still happens.

### 3.4 Semantic colour usage

| Colour | Means | Never means |
| --- | --- | --- |
| `--success` | Connected, complete, healthy | "the AI was right" |
| `--warning` | Degraded, needs attention, paused | decoration |
| `--danger` | Failed, destructive, excluded | a priority badge |
| `--info` | Neutral informational state | the accent |
| `--accent` | Selected, focused, primary action | decoration, background wash |

Priority uses its own four-tier ramp (`--priority-{urgent,high,medium,low}-{bg,fg}`) and
must never borrow the semantic hues for a badge. Existing `badge-urgent` / `badge-high`
/ `badge-neutral` classes already do this correctly.

## 4. Typography

Existing scale in `styles/tokens.css:33-49` is **good and is preserved as-is**. Eight
steps, one ratio, consistent leading:

| Token | Size | Use |
| --- | --- | --- |
| `--text-xs` | 11.5px | metadata, counts, timestamps |
| `--text-sm` | 13px | secondary body, table cells |
| `--text-base` | 14px | **body default** |
| `--text-md` | 15.5px | message subject, emphasised body |
| `--text-lg` | 17.5px | panel titles |
| `--text-xl` | 20px | page titles |
| `--text-2xl` | 23px | reader subject |
| `--text-3xl` | 27px | briefing headline |

Leading: `--leading-tight 1.3`, `--leading-normal 1.5`, `--leading-relaxed 1.68`,
`--leading-reader 1.66`. The dedicated reader leading is a good decision — long-form
mail needs more air than UI chrome.

Families: `--font-sans` leads with `Segoe UI Variable Text`, which is the correct
Windows-native choice and means **no webfont is shipped**. Zero font bytes in the bundle.
`--font-mono` uses Cascadia Code for diagnostic codes and search operators.

## 5. Spacing

Scale in `tokens.css:23-30`: `--space-1 4px` through `--space-10 40px`. Four-pixel base,
no odd values. Gaps of 7 and 9 are absent and must not be invented — pick 6 or 8.

Layout constants: `--rail-width 56px`, `--header-height 52px`, `--mail-pane-width
336px`, `--intel-pane-width 336px`. These are honest numbers for a dense mail tool and
are kept.

## 6. Radii

`tokens.css:15-20`: `--radius-xs 2px`, `-sm 4px`, `-md 6px`, `-lg 10px`, `-xl 14px`,
`-full 9999px`.

Application: `--radius-sm` for inputs, chips, and small buttons; `--radius-md` for
panels and cards; `--radius-lg` for dialogs; `--radius-full` **only** for a genuinely
circular control (the status dot, the avatar). `--radius-xl` is currently unused and is
reserved for marketing surfaces on the website, not in the app.

The failure mode this prevents is the "giant rounded container everywhere" look: Alfred
is dense, so most of its surface area is at `4-6px`.

## 7. Borders and shadows

Border scale: `--border-subtle` (dividers), `--border-default` (panel edges),
`--border-hover` (interactive), `--border-focus` (focus ring, 2 layers so it works on
any background). Four steps is the right number; a fifth means something is wrong.

Shadow scale: `--shadow-1` (resting card), `--shadow-2` (raised), `--shadow-3`
(overlay/dialog), plus `--shadow-accent` for a primary action. Shadows are for
elevation, not for glow. The ambient layer is not a shadow.

## 8. Icons

One library: **Lucide**, used consistently across 30+ components, `strokeWidth={2}`,
`size={18}` in the rail. Zero emoji anywhere. This is correct and is preserved — see
`docs/Rules.md` §3.

Icon-only controls must carry an accessible name. `aria-label` is the mechanism;
`title` is a tooltip and is not sufficient. Phase 3 audits the 22 `title=` usages in
`MessageReader.tsx`, `MessageRow.tsx`, and `IconRail.tsx`.

Brand assets are a separate deliverable and are currently placeholders (F8): eight of
ten tracked icon files self-declare as generated placeholders in
`tools/generate_icons.py:1-8`; `16x16.png` and `48x48.png` are Tauri-init defaults the
generator does not even write; `icon.svg` is a third, different artwork with an
envelope-in-A motif that appears in no raster file; `desktop/branding/` does not exist;
`frontend/scripts/derive-brand-assets.ps1` has never been run. Required set: app icon,
installer icon, taskbar icon, splash mark, light and dark marks, monochrome mark,
favicon, OG image, social share image.

## 9. Component hierarchy

```
App
├── StartupGate            readiness, failure, retry, diagnostics
├── IconRail               6 destinations, 2 groups, service status
├── WorkspaceHeader        context, search, AI status, account
└── main.workspace-content
    ├── OverviewPage       briefing + attention + metrics
    ├── MailWorkspace      the default view
    │   ├── MailPane       view switch, category tabs, toolbar, MessageList
    │   ├── MessageReader  subject, meta, body, attachments
    │   └── IntelligencePanel  analysis, tasks, deadlines, draft
    ├── TasksPage
    ├── DeadlinesPage
    ├── AccountsPage
    └── SettingsPage
    └── AnalysisProgress   always mounted, self-hiding
```

Shared primitives belong in `src/components/ui/`. Today that directory contains one
component (`AnalysisProgress.tsx`) and the rest of the UI is hand-rolled per feature.
Phase 3 decides whether to introduce a small primitive set (Button, Dialog, Field,
Tooltip, Toast) or to keep the current explicit approach — but it may not be left
half-committed with a shadcn `components.json` and zero shadcn components.

## 10. States

Every interactive element defines all of these. No exceptions.

| State | Requirement |
| --- | --- |
| Rest | Token-based; never a hardcoded hex in a component |
| Hover | `--border-hover` or a `--motion-hover` background shift |
| Focus-visible | 2px double ring: `0 0 0 2px var(--bg-app), 0 0 0 4px var(--border-focus)`. Already implemented at `globals.css:2550-2565`. Correct — preserve it. |
| Active | `--accent-active`, no layout shift |
| Disabled | `opacity: .5; cursor: not-allowed` (already in `reset.css`) **and** `aria-disabled` where it is not a real `<button disabled>` |
| Loading | Skeleton for content, spinner for an action in flight, never a spinner over content that is already readable |
| Empty | Explains why it is empty and offers the one action that fixes it. `empty-state` class exists and is used. |
| Error | Plain message, a diagnostic code, a retry, and a log path. Never a raw exception string. |
| Success | Toast, auto-dismissing, never blocking. |
| Selected | `--bg-row-selected` + `aria-selected` / `aria-current` |

`globals.css:441-455` styles `.pane-separator:focus-visible` separately because the
resizable-panels separator is neither a `<button>` nor `[role=button]` and so escapes
the global focus rule. That is the right fix and the pattern to follow for any
non-standard focusable.

## 11. Light and dark themes

Both themes are complete and hand-tuned today (60 properties each in `themes.css`), with
`color-scheme` set correctly per theme and a pre-paint inline script in `index.html` that
applies the stored preference before first paint, so there is no theme flash. This is a
good implementation and is preserved.

Dark mode is not an inversion. It uses a cool near-black app (`#0b0d13`), a distinct
panel (`#131620`), and a separate reader surface (`#151a24`), so the reading surface is
distinguishable from the chrome around it in both themes.

`ThemeToggle` uses `role="radiogroup"` / `role="radio"` with `aria-checked` but has no
arrow-key handling and no roving tabindex. A radiogroup without keyboard semantics is
worse than three plain buttons. Fixed in Phase 3.

## 12. Motion

Existing tokens, all preserved:

| Token | Duration | Curve | Use |
| --- | --- | --- | --- |
| `--motion-micro` | 110ms | `cubic-bezier(.2,0,0,1)` | state flips, hover |
| `--motion-hover` | 150ms | `cubic-bezier(.2,0,0,1)` | hover transitions |
| `--motion-pane` | 220ms | `cubic-bezier(.22,1,0,.36)` | pane resize, disclosure |
| `--motion-reveal` | 300ms | `cubic-bezier(.22,1,0,.36)` | list entry |
| `--motion-spring` | 420ms | `cubic-bezier(.22,1,0,.36)` | dialog entry |

Reduced motion is handled in two places — the tokens are zeroed inside
`prefers-reduced-motion` (`tokens.css:70-78`) and a global `!important` override kills
all animation and transition durations (`motion.css:76-83`). Belt and braces; correct.

Removed in Phase 3: `drift-a/b/c` (110-140 s ambient orb loops). Retained: `reveal-up`,
`pane-in`, `slide-up`, `shimmer` (skeletons), `spin`, `underline-in`, `soft-pulse`.

No JavaScript-side reduced-motion check exists. If Phase 3 or 4 introduces motion that
JS must also suppress (for example a JS-driven progress animation), a
`matchMedia('(prefers-reduced-motion: reduce)')` check is required at the same time.

## 13. Accessibility

### Baseline that already holds
- Semantic elements throughout; 136 ARIA attributes, used to fill real gaps
- Visible focus on every focusable, including non-standard focusables
- `prefers-reduced-motion` honoured in CSS
- Roving tabindex on the category tablists with full arrow/Home/End support — a correct
  APG implementation
- Focus trap **and focus restore** in the only dialog (`SourceEmailPreview.tsx:47-91`),
  covered by four tests
- External link protocol allow-listing in `lib/urlSecurity.ts`, covered by eleven tests
- `aria-live` on the readiness gate and analysis progress

### Gaps, in priority order
1. **`--text-muted` and `--text-faint` fail WCAG AA** — §3.1, seven tokens. Blocking.
2. **No skip-to-content link.** Zero occurrences in the frontend. Blocking for keyboard
   users, since the rail plus header plus search precede every page's main content.
3. **The default view has no `<h1>`.** Mail is the landing page and its only heading is
   the reader's `<h2>`. Every other page has a `.page-title` heading.
4. **No focus movement on navigation.** Changing page via the rail does not move focus
   to the new heading; selecting a message does not move focus to the reader.
5. **Zero `aria-describedby` / `aria-labelledby` / `aria-expanded` / `aria-controls`.**
   The search input, the theme radiogroup, and the disclosure panels all need them.
6. **`ThemeToggle` radiogroup** has no arrow-key handling (see §11).
7. **`aria-label` on a decorative `<svg>`** at `MailWorkspace.tsx:421` is not reliably
   exposed because the element has no `role="img"`.
8. **AI status is not announced.** The header status chip and the rail status dots
   change state but are not live regions.
9. **The startup status chip reads `Ctrl K` unconditionally**, which is wrong for
   Cmd-K users on macOS — and the app is Windows-only today, so this becomes correct by
   being Windows-specific, not by being platform-sniffed.
10. **Focus trap exists in one dialog only.** Every future dialog needs the same
    treatment; a shared primitive is the way to guarantee that.

### Target
WCAG 2.1 AA for the application. A keyboard-only pass and a screen-reader pass over
every page, recorded as evidence in the Gate 3 report.

## 14. Responsive behaviour

Alfred is a desktop window with `minWidth: 900` / `minHeight: 650`, so the requirement is
"graceful at reduced window widths", not "mobile".

Current state: one window-level media query at `max-width: 1100px` (`globals.css:2163`)
and four container queries — `mail-pane` at 520px and 360px, `mail-workspace` at 900px
and 600px.

**Container queries are the correct choice here** and are preserved: a resizable pane
must respond to its own width, not the window's. This is a genuinely good decision
already made in the codebase.

Requirements:
- No horizontal overflow at 900px width, in either theme, on any page
- No horizontal overflow of the reader body for long URLs, long unbroken tokens, or wide
  tables — `overflow-wrap` is required, not optional
- The icon rail stays fixed; the intelligence pane collapses below its container
  breakpoint
- Dialogs clamp to the viewport with a margin on every side
- The public website is separately responsive and is specified in Phase 6

## 15. What Phase 3 must verify before this document is considered implemented

- [ ] Every colour token in §3.2 measured in both themes against every background it is
      actually used on, not just the three reference backgrounds
- [ ] Zero usages of `--text-faint` as text colour
- [ ] Zero `.text-muted` usages that resolve below 4.5:1
- [ ] Ambient orb layer removed from `surfaces.css` and `App.tsx`
- [ ] Glass token count reduced to two surfaces
- [ ] Tailwind import and the four unused Tailwind-family dependencies removed
- [ ] Real brand asset set generated and installed (§8)
- [ ] Skip-to-content present and keyboard-reachable
- [ ] `<h1>` on every page including Mail
- [ ] Focus movement on page change and message selection
- [ ] `ThemeToggle` keyboard-correct
- [ ] No console errors (this is the F20 React warning as well)
- [ ] Keyboard-only and reduced-motion passes recorded
