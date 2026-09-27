# Alfred — Phase 1 Visual QA Record

Date: 2026-09-27
Branch: `feature/mail-workspace-productization-20260907`
Baseline commit: `ec688c0` — `feat(alfred): complete keyboard focus management`

This is the first attempt to *look at* the running application rather than assert
about it from tests. It is deliberately incomplete, and the gaps are listed as
plainly as the findings.

---

## Environment

| | |
| --- | --- |
| OS | Windows 11 Home Single Language, build 26200 |
| Display | 3840×2160 physical, 2560×1440 logical (**150% scaling**) |
| Session | Interactive desktop (`explorer.exe` running) |
| Screenshot method | `System.Drawing` `Graphics.CopyFromScreen` via PowerShell, after `SetProcessDpiAwarenessContext(PER_MONITOR_AWARE_V2)` |
| App execution mode | **Packaged release build** — `cargo tauri build` from `desktop/`, run from `target/release/alfred-desktop.exe` with its own backend sidecar. Not a Vite preview, not component screenshots. |
| Data | A **real connected Gmail account** was present (982 inbox messages, real correspondents). Nothing was mocked. |
| Window sizes | **Not** completed. See *What was not inspected*. |
| Light / dark | **Light only.** Dark mode was not reached. |

Artifacts are under `%TEMP%\opencode\qa\`. They are intentionally **not** committed:
they contain real mailbox content.

---

## Confirmed issues

### A1 — The release build did not compile at all (severity: blocking)

`cargo build` and `cargo build --release` both failed:

```
error[E0425]: cannot find function `set_boxed_logger` in crate `log`
error: could not compile `alfred-desktop` (bin "alfred-desktop")
```

**Cause.** `desktop/src-tauri/Cargo.toml` declared `log = "0.4"` with no features.
`log::set_boxed_logger` (called at `main.rs:918`) lives behind the `std` feature, and
nothing in the runtime dependency graph enabled it.

**Why it survived.** `cargo test` passed 35/35 the whole time. Cargo unifies features
across **dev-dependencies** in a test build, and `tauri-cli` (a dev-dependency) pulls in
something that enables `log/std`. A normal build has no dev-dependencies, so the feature
was absent. The test suite was compiling a different feature set from the shipping
binary — so every "Rust: 35 passed" line in previous gates was true and misleading.

**Rule.** Spec §16 implementation order requires each step to be verified; a target
that cannot be built cannot be verified at all.

**Fix applied.** `log = { version = "0.4", features = ["std"] }`, with a comment
recording the trap. `cargo build --release` and `cargo tauri build` now both succeed and
the NSIS installer is produced.

### A2 — A bare `cargo build --release` binary serves no frontend (severity: high, now avoided)

Running the binary produced Chromium's own error page inside the Alfred window:

> **Hmmm... can't reach this page** — localhost refused to connect. `ERR_CONNECTION_REFUSED`

The correct build path is the Tauri CLI from `desktop/` (`cargo tauri build`), which
embeds `frontend/dist`. `npx tauri build` also fails here — `tauri-cli` is a *Rust*
dev-dependency, not an npm package, so the binary is `cargo-tauri.exe`.

**No code change.** This is a build-invocation trap, now documented here. Worth a
repository note so the next person does not lose an afternoon to it.

### A3 — Message snippets show raw HTML entities (severity: medium, content)

Visible in the list at real width:

> `Hi Nipun, I wanted to check in with you one final time if you&#39;re doing…`

`&#39;` is rendered literally instead of an apostrophe. The snippet path
(`MessageRow.bodySnippet` → `source_metadata.gmail_raw.snippet`, else the first body
line) passes the text through untouched, and the stored text carries an escaped
apostrophe. Whether the fix belongs in the Gmail normaliser or at render time is a
backend decision, so **not fixed here** — recorded for the normaliser task.

---

## What was actually inspected

Only the following, at approximately **1440 logical px, light theme, Mail view**:

- Application shell: grid, header/content split, no stray scrollbars.
- Sidebar: ~232px, three uppercase section groups (MAIL / INTELLIGENCE / SYSTEM),
  ten labelled items with icons, active **Inbox** carrying the accent left bar and a
  right-aligned `982` count.
- Header: `Mail` + `Gmail inbox` subtitle, search field with leading icon, placeholder
  *Search all mail*, and a `Ctrl K` hint chip. Sync, *AI ready* and account controls
  present on the right.
- Mail pane head: `Inbox` title; category tabs `Primary 80`, `Promotions 77`,
  `Social 2`, `Updates 823`, `Forums 0`; *All mail synced*; filter row
  (All / Important / Reply / Later / refresh) and a *Filter inbox* field.
- Message rows: sender, subject, one-line snippet, `IMPORTANT` / `REPLY` badges,
  right-aligned date, hairline separators, and the teal unread bar on the left edge of
  the first row — visible at rest, as §9.5 requires.
- Reading pane **empty state**: envelope glyph and "Select a message to read it."
- The floating `Analyzing 307 messages · Local AI ready` progress bar, which sits over
  the bottom of the list.

Overall the shell reads as a calm, dense, professional mail client. No layout collapse,
no missing panes, no unstyled regions.

---

## What was NOT inspected

Stated plainly, because the temptation to assume is exactly what this gate exists to
prevent. **None of the following was seen, and no claim is made about any of it.**

- **The reading pane with a message open** — the single most important target. The
  subject, the From/To/Date grid, the 68ch measure, attachments and the action row were
  **never rendered on screen**. Only the empty state was seen.
- **The intelligence panel with real content** — never opened. The borders, radius and
  separation restored by the dead-CSS gate are therefore still unverified.
- **Accounts, Settings, Overview, Tasks, Deadlines** — not visited.
- **Dark mode** — not reached at any point.
- **Error, empty, retry, AI-unavailable, syncing, authentication-required states** — not
  triggered.
- **Window sizes.** No capture is trustworthy at 1100 / 1000 / 900 / 800 logical. The
  1100px-class rail collapse and the 900px intelligence padding compression are
  therefore **unverified**, as is graceful degradation below the 900px `minWidth`.
- **Keyboard behaviour** — Ctrl+K, the skip link, arrow navigation, and Enter-to-open
  were verified by tests in UI-10, not by eye.

### Why the pass stopped short

Two environment problems, both worth recording:

1. **DPI-unaware capture produced false defects.** The first captures showed black
   horizontal bands and duplicated, offset panes — which looked exactly like a severe
   layout bug. They were an artifact: an unaware process receives *logical* rects from
   `GetWindowRect` but `CopyFromScreen` reads *physical* pixels, so the capture was a
   mis-scaled crop. After opting into per-monitor DPI awareness the bands disappeared
   completely. **This is why the bands are not reported as a defect.**
2. **Window automation was unreliable.** Programmatic `MoveWindow` calls left the window
   collapsed to 199×34 on several attempts, and foreground focus was repeatedly lost to
   other applications, producing captures of the desktop rather than the app. Driving
   mouse input to open a message and visit other pages did not complete reliably.

Continuing to fight the window manager would have produced a longer list of
untrustworthy screenshots, which is worse than a short honest one.

---

## Deferred issues

| Item | Why deferred | Intended task |
| --- | --- | --- |
| Reading pane with a message open | Never rendered on screen | Repeat this gate |
| Intelligence panel content | Never rendered on screen | Repeat this gate |
| Dark mode | Not reached | Repeat this gate |
| Accounts / Settings / Overview / Tasks / Deadlines | Not visited | Repeat this gate |
| 1100 / 1000 / 900 / 800px behaviour | No trustworthy capture | Repeat this gate, ideally on a 100%-scale display |
| Error / empty / AI-unavailable states | Not triggered | Repeat with a deliberately failing backend |
| Snippet HTML entities (A3) | Fix belongs in the Gmail normaliser | Backend normalisation task |
| `cargo build --release` serves no frontend (A2) | Build-invocation trap, not a code defect | Repo docs |
| Message list is not keyboard navigable | Interaction-model change, out of scope | Dedicated listbox task |
| AI-state vocabulary consolidation (4 remaining) | Not visually problematic | Cleanup task |
| Intelligence-panel off-scale values (`6px 0`, `3px` nudge) | Not visually inspected | Needs the panel rendered first |
| `.section-label` 10px / 0.09em vs spec 10.5px / 0.04em | Section labels *were* seen in the sidebar and read acceptably at real size; not visually problematic | Separate typography decision |
| Remaining inline `style` objects | Not visually problematic where seen | Cleanup task |
| `Ctrl+1..6` and `?` overlay | Not started | Keyboard shortcut task |
| Real brand assets | Placeholder; taskbar icon shows a generic purple "A" tile | Branding task |
| 3.2s looping status pulse | Not observed as distracting | UI-11 motion decision |
| `.badge-reply` accent colour | `REPLY` badge rendered teal; legible and not garish | Design decision |
| `#f28b82` fallbacks | Never paint | Cleanup task |

---

## Manual verification

**What I actually did:** built the release app, ran it, and looked at the Mail view at
roughly 1440 logical px in light theme with a real mailbox, via screen capture of the
running window. Roughly a dozen captures were taken; the analysis above is based only
on the ones I could trust after diagnosing the DPI artifact.

**What I did not do:** open a message, visit any other page, switch theme, resize
reliably, or trigger any error state.

**Status:**

- Automated verification: **PASS** — 657 tests, 0 failures.
- Manual visual verification: **PARTIAL** — Mail view, light theme, one size only.
- Gate 1 packaged-app verification: **STILL NOT PASSED.** The build now works and the
  app launches, which was the blocker, but a packaged *install* was not performed and
  `desktop.log` plus a post-quit `tasklist` check have not been captured.
