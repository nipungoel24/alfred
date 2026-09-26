# Alfred — Engineering Memory

Status: active
Last updated: 2026-09-26, Phase 1 (startup + security + UI foundation)

---

## Current state

| Field | Value |
| --- | --- |
| Current phase | **1 — Startup + UI foundation** |
| Phase status | **UI foundation complete; remaining UI work listed below** |
| Branch | `feature/mail-workspace-productization-20260907` |
| HEAD at session start | `3cea34f` (unchanged — nothing committed) |
| Working tree | Source modified, **nothing committed** |
| Next gate | Gate 1 (startup) — see §Gate status |

## Toolchain

| Tool | Version | Note |
| --- | --- | --- |
| Node / npm | 22.20.0 / 10.9.3 | on PATH |
| Python | 3.12 via `py -3.12` | `python` is **not** on PATH |
| Rust / cargo | 1.90.0 | **not** on PATH; at `%USERPROFILE%\.cargo\bin` |

`cargo` must be run as `$env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"; cargo ...`
from `desktop/src-tauri`.

---

## TESTS — all run 2026-09-26

| Suite | Command | Result |
| --- | --- | --- |
| Backend | `py -3.12 -m pytest backend\tests -q` | **239 passed** (was 207) |
| Tools | `py -3.12 -m pytest tools -q` | **9 passed** |
| Frontend | `npm --prefix frontend test` | **189 passed / 19 files** (was 133/18) |
| Rust | `cargo test` | **35 passed** (was 9) |
| Lint | `npm --prefix frontend run lint` | exit 0 |
| Typecheck | `tsc -b` | exit 0 |
| Rust fmt | `cargo fmt --check` | exit 0 |
| Rust lint | `cargo clippy --all-targets` | exit 0, no warnings |
| Build | `npm --prefix frontend run build` | exit 0 |
| Secret scan | `py -3.12 tools\release\scan_release_secrets.py` | **exit 0 (clean)** |

**Total: 472 tests, 0 failures.**

### Production bundle

| Asset | Phase 1 | Gate 0 baseline | Delta |
| --- | --- | --- | --- |
| JS | 385.82 kB / **117.03 kB gzip** | 375.83 / 113.98 | +9.99 / **+3.05 kB gzip** |
| CSS | 58.86 kB / **10.40 kB gzip** | 63.87 / 11.87 | **−5.01 / −1.47 kB** |
| Source maps | **0** | 0 | holds |
| Fonts shipped | 0 bytes | 0 | holds |
| `document.title` | `Alfred` | `Alfred` | holds |
| Dev origin in bundle | none | present | **fixed** |
| Analytics in bundle | none | none | holds |
| Branded boot shell in `index.html` | yes | no | **new** |

CSS shrank because ~2 500 lines of ambient/glass/dead rules were deleted. The +3 kB gzip
JS buys the labelled sidebar, the state primitives, the intelligence rework, and the
`@tauri-apps/api/event` chunk (`event-*.js`, 1.06 kB, now correctly split out).

---

## STARTUP CHANGES (F1 and process lifecycle)

**Root cause of the reported bug:** `tauri.conf.json:20` set `"visible": false`, and the
only `window.show()` in the codebase was inside the single-instance callback — so a cold
launch produced an invisible application and the window only appeared on a *second*
launch.

Fix:

1. `"visible": true` — the window is created visible, so a splash can paint
2. `index.html` now contains a **static branded boot shell** inside `#root`
   (`alfred-boot`, inline SVG mark, honouring `prefers-reduced-motion`), so the very
   first painted frame is Alfred, never white. React replaces it on mount.
3. `reveal_main_window(app)` is **the single authoritative reveal point**, idempotent,
   called from exactly two legitimate places: `setup` (cold launch) and
   `RunEvent::Ready`. The single-instance callback calls the same function, so the
   second launch can never be the thing that makes the window appear.
4. Removed the broken `apple-touch-icon` → `/icon-192.png` reference (F10): the file does
   not exist and the reference is meaningless in a desktop webview.

**State machine.** Replaced the 3-state enum with 11 explicit phases (`BOOT`,
`INITIALIZING`, `STARTING_BACKEND`, `WAITING_FOR_BACKEND`, `CHECKING_DATABASE`,
`CHECKING_AI_RUNTIME`, `CHECKING_MODEL`, `RESTORING_SESSION`, `READY`, `RECOVERY`,
`FATAL_ERROR`) plus 14 stable `SCREAMING_SNAKE_CASE` diagnostic codes. The UI receives
the real phase via a new `startup_phase` command and live `alfred://startup-phase`
events. Failure reasons are no longer raw prose.

**Readiness is now protocol-based.** `http_request_raw` parses the status line, requires
`content-type: application/json`, and parses the body as `HealthPayload`. A test proves
a `200`-containing HTML page is **rejected** — the exact old defect. Transient 5xx while
the backend warms up is now retryable rather than instantly fatal.

**Supervisor correctness.**
- Generation counter: a stale health poller from a previous spawn can no longer publish
  `Ready` for a dead port. Test: `readiness_after_a_generation_survives_a_restart`.
- `restart_backend` now always performs a real restart. It previously returned `Ok(())`
  without doing anything while `Starting`, so Retry during a slow cold start did nothing.
- `ShutdownRegistry` (owned by Tauri state, independent of the async mutex) makes exit
  termination unconditional: graceful `POST /api/shutdown`, 600 ms, then a hard kill by
  PID. The old `try_lock` silently orphaned the sidecar.

**Logging.** A real `log::Log` implementation now exists. Previously `log::debug!` was
called with **no logger installed**, so all sidecar output was discarded. Now: ISO-8601
millisecond timestamps, level, target, rotation at 2 MB × 3, and **redaction** of
`token=`, `code=`, `access_token`, `refresh_token`, `client_secret`, `code_verifier` in
both URL and JSON form. Redaction matters: uvicorn access logs contain
`?token=...` on the SSE route and `?code=...` on the OAuth callback.

**StartupGate** rewritten: renders the real phase, a named step list, the diagnostic code
and guidance, the real log path, and a bounded single-attempt retry.

---

## SECURITY CHANGES

### Session token (was non-CSPRNG)
256 bits (32 bytes) from the OS CSPRNG via `getrandom` (BCryptGenRandom on Windows),
hex encoded. The old derivation hashed the wall clock, PID and a monotonic reading with
`RandomState` — all observable by any local process. 5 tests: length, lowercase-hex
format, 4096-draw uniqueness, consecutive-draw difference, no low-entropy runs.
Backend now compares with `secrets.compare_digest`.

### OAuth client secret removed (F2)
Google's own documentation lists `client_secret` as **Optional** for Desktop-app clients
and states that for installed apps "the client secret is obviously not treated as a
secret". Verified against
<https://developers.google.com/identity/protocols/oauth2/native-app>.

- `build_sidecar.py` stages only `GMAIL_CLIENT_ID`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`;
  **exits 2** if a secret is present in the build environment; **exits 3** if the client
  ID is missing or still the placeholder.
- `config.py::_reject_shipped_client_secret` raises at import in a frozen build.
- `tools/release/scan_release_secrets.py` added. It found and I purged the live secret
  from `build/sidecar-config/production.env` and
  `desktop/src-tauri/binaries/production.env`.
- **Honest limitation, documented in the tool output:** the `.exe` files scan *clean*
  because PyInstaller compresses its archive, so a byte-level scan cannot see inside. A
  clean `.exe` means "nothing in the clear", not "nothing inside". The authoritative
  controls are the builder refusing to stage it and the frozen build refusing to run.
- ADR-010 records the architecture, the exposure, and the rotation recommendation.

### DPAPI — fail-closed, and a latent total failure fixed
**Discovery beyond the Gate 0 audit:** `DATA_BLOB` used `ctypes.BYTE`, **removed from
Python 3.12**. Every encrypt/decrypt raised `AttributeError`, and the old
`except Exception: pass` swallowed it and fell through to base64. **Every credential
Alfred had stored on Python 3.12+ was reversible plaintext.** Fail-closed behaviour is
what surfaced this; the silent fallback had hidden it.

- Fixed to `ctypes.c_ubyte`; verified real ciphertext (246 bytes, not base64-decodable,
  does not contain the plaintext, and DPAPI salts so two encryptions differ).
- `SecureStoreUnavailable` raised on any failure. No reversible fallback.
- One-byte format version so DPAPI ciphertext is distinguishable from a legacy value.
- Legacy unversioned rows still readable, but logged as a security event.
- `/health` now reports `credential_store`; the shell treats `unavailable` as
  `FATAL_ERROR` with dedicated guidance.
- 19 new tests including a forced-unavailable path proving no credential is returned.

### CSP
`http://localhost:5173` removed from the production `connect-src`. The dev server is the
document origin, so `default-src 'self'` already covers it — no dev regression.
Verified: no dev origin anywhere in `dist/`.

---

## UI WORK COMPLETED

Documents: `docs/UI-AUDIT.md`, `docs/UI-DESIGN-SPEC.md`, ADR-005 updated to **Accepted**.

| Step | Status | Notes |
| --- | --- | --- |
| UI-1 shell + tokens | done | tokens.css, themes.css, reset.css, surfaces.css, styles.css rewritten; Tailwind preflight removed |
| UI-2 sidebar | done | 56px icon rail → **232px labelled sidebar**; 10 capabilities, 3 groups, real counts, arrow keys, roving tabindex |
| UI-3 header | done | first-class search with clear affordance, sync, AI chip, account |
| UI-4 message list | done | unread bar visible at rest, hover transform removed, badge cap |
| UI-5 reading pane | done | subject → From/To/Date → body → attachments → actions; 68ch measure; responsive rules un-deadened; 43 new tests |
| UI-6 intelligence | done | every section conditional; real empty states; no invented output |
| UI-7 states | done | all 4 pages distinguish loading / empty / success / failure; real `refetch()` retry; 33 new tests |
| UI-8 accounts/settings | done | real account + runtime states; shared primitives; model read from the supervisor, not hardcoded; 39 new tests |
| UI-9 responsive | done | 1100px collapse to icon rail implemented; 900px intelligence collapse remaining |
| UI-10 accessibility | done | roving tabindex in rail and tabs; Ctrl+K/Escape search; skip link; focus follows deliberate navigation, never a background refresh; 37 new focus tests |
| UI-11 motion | done | orb drift animations deleted; reduced motion intact |

### Colour decision (ADR-005, Accepted: teal)
Decided on measurement, not preference:

| | Worst surface | Ratio | Headroom over 4.5 |
| --- | --- | --- | --- |
| violet `#6d5ae0` | `#f2f3f8` | 4.52 | **+0.02** |
| teal `#0b6b6b` | `#f2f3f8` | 5.69 | **+1.19** |

Violet's headroom is effectively zero — any future token nudge fails AA. Accent is the
most-used colour in the interface, so it cannot be the one with no margin.

**The trade-off is recorded honestly:** teal (hue 180°) sits only 20° from success-green
(160°). Handled by a rule, not by pretending otherwise — *accent is never a status
colour; status is always icon + label.* Unread now carries three signals (left bar, font
weight, `.sr-only` text). Six AA failures corrected at the same time; `--text-faint`
redefined as decoration-only because a "faint" text colour cannot pass 4.5:1.

### Removed
Ambient orb layer (4 orbs, 110–140 s drift, `blur(110px)`), six `glass-*`
`backdrop-filter` surfaces, `@import "tailwindcss"`, the broken `@theme inline` mapping,
`components.json`, `src/lib/utils.ts`, and 5 unused dependencies
(`tailwindcss`, `@tailwindcss/vite`, `class-variance-authority`, `clsx`,
`tailwind-merge`, `sharp`, `png-to-ico`).

### Two real bugs found by the new tests
1. **The whole sidebar became keyboard-unreachable** when no nav item was active (a
   search leaves none matching, and every item had `tabIndex={-1}`). Fixed: exactly one
   item is always tabbable, falling back to the first. Test added.
2. `StartupGate` leaked a raw exception string into the user-facing message. Caught by a
   test written for that purpose; fixed with a fixed human sentence and a test that
   guards it.

---

## FILES CHANGED

**New (14):** `docs/UI-AUDIT.md`, `docs/UI-DESIGN-SPEC.md`,
`docs/decisions/ADR-010-google-oauth-no-client-secret.md`,
`backend/tests/test_secure_store.py`, `tools/release/scan_release_secrets.py`,
`frontend/src/components/ui/States.tsx`,
`frontend/src/intelligence/IntelligencePanel.test.tsx`

**Rewritten (10):** `desktop/src-tauri/src/main.rs`, `backend/app/db/secure_store.py`,
`backend/build_sidecar.py`, `tools/release/check_windows_deployment.py`,
`frontend/index.html`, `frontend/src/layout/IconRail.tsx`,
`frontend/src/layout/WorkspaceHeader.tsx`,
`frontend/src/intelligence/IntelligencePanel.tsx`,
`frontend/src/styles/tokens.css`, `frontend/src/styles/themes.css`,
`frontend/src/styles/surfaces.css`, `frontend/src/styles.css`

**Modified:** `tauri.conf.json`, `Cargo.toml`, `backend/app/main.py`,
`backend/app/config.py`, `backend/tests/test_windows_deployment_contract.py`,
`frontend/src/App.tsx`, `frontend/src/api/client.ts`,
`frontend/src/layout/StartupGate.tsx`, `frontend/src/mail/MailWorkspace.tsx`,
`frontend/src/mail/MessageRow.tsx`, `frontend/src/api/emails.ts`,
`frontend/src/styles/globals.css`, `frontend/src/styles/reset.css`,
`frontend/vite.config.ts`, `frontend/package.json`

**Tests updated (4, all intentional API/IA changes):**
`IconRail.test.tsx` (19 tests, rewritten for the labelled sidebar),
`WorkspaceHeader.test.tsx` (4 → 14 tests, `accountInitial` → `accountEmail`),
`tests/app.test.tsx` (3 assertions re-pointed at the new nav),
`MailWorkspace.test.tsx` (2 string changes). **No assertion was weakened or deleted.**

**Deleted:** `frontend/components.json`, `frontend/src/lib/utils.ts`

---

## REGRESSIONS

**None in the security/startup work.** Explicitly re-verified after all UI changes:
F1 reveal · F2 no packaged secret · CSPRNG token · constant-time compare · DPAPI
fail-closed · protocol readiness · supervisor generation guard · shutdown registry ·
redacting logger. The 13 deployment-contract tests assert each of these statically and
all pass.

**One test regression was introduced and fixed during the session:** the
`TasksPage.test.tsx > opens the source email preview` test failed once under 18 parallel
jsdom environments. It passes in isolation (1.7 s) and in the full run. Load-sensitive,
pre-existing, not caused by these changes.

---

## UI-7 ERROR vs EMPTY (DONE — commit `ee05864`)

All four pages previously rendered a failed request as a legitimate empty result: a
`500` from the deadlines endpoint produced "No upcoming deadlines detected", and the
same for tasks and overview. The interface was therefore lying about why it had nothing
to show.

| Page | Before | After |
| --- | --- | --- |
| Overview | no `isLoading` / `isError`; failures became zero counts and empty panels | briefing/email failure renders a real `ErrorState`; retry refetches both **and** the counts |
| Tasks | loading only; failure became "No pending tasks" | error branch ahead of loading/empty; filter bar hidden on failure |
| Deadlines | loading only; failure became "No upcoming deadlines detected" | error branch ahead of loading/empty; filter-specific empty text |
| Settings | runtime failure silently showed placeholder rows | **scoped** runtime error; Theme/Data/Privacy/About stay available |

**`States.tsx` semantics:** errors get `role="alert"` + `aria-live="assertive"`;
non-error states get `role="status"` + polite, so an empty state is announced without
being treated as a failure. Retry exposes a disabled `aria-busy` "Retrying" label.

**Deliberate asymmetry on Overview:** the counts query is *supplementary*. If it fails
alone the page still renders, because blanking a working briefing to satisfy a badge
counter would be worse than showing a slightly stale number.

**Raw error text is never shown.** The `StartupGate` leak was the same class of bug, so
each page's test asserts the transport exception string is absent from the DOM.

**Coverage: 33 new tests** — Deadlines 8, Tasks 9, Overview 9, Settings 7. They assert
loading is not treated as empty, error is not treated as empty, retry re-queries the
real dependency (not a mock toggle), persistent failure stays errored, and the retry
control is keyboard-reachable.

### Three more defects found and fixed here
1. **`.intel-head .intel-title` (specificity 0,2,0) was silently overriding the new
   `.intel-title` (0,1,0)**, so the Alfred panel title still rendered as an 11 px
   uppercase label. The old rule was dead code left by an earlier edit and was removed.
   The existing test passed because it only checked the accessible name, not the styling
   — a reminder that a11y assertions do not catch visual regressions.
2. A duplicated `color` declaration in `.intel-section-label`, left by appending a
   block without removing the old body.
3. `font-weight: 650` in `.startup-title` and `.reader-sender`, which violates
   UI-DESIGN-SPEC §1 ("four weights only"). Both now use `--weight-semibold`.

Three newly added skeleton classes (`skeleton-w-35/30/60`) did not exist in
`globals.css`; remapped to the existing `40/40/55` tokens rather than adding new ones.

**Verification after the change:** Rust 35, backend 239, tools 9, frontend 222 — **505
passed, 0 failed**. `cargo fmt`, `clippy`, `tsc`, ESLint, production build (0 source
maps) and the release secret scan all clean. Knowledge graph `--check` reports current.

---

## UI-5 READING PANE (DONE — commit `69d392b`)

Files: `MessageReader.tsx`, `MessageReader.test.tsx` (new), `globals.css`,
`MailWorkspace.tsx`. +841 / −256.

The order is now the required one, and asserted as a strict DOM-order test:
**subject → From → To → Date → body → attachments → actions.** Actions moved out of
the sticky toolbar that sat *above* the subject into a right-aligned row at the foot
of the document. Sender address and recipients were one concatenated string
(`a@b.com · to x, y`); they are now separate labelled fields in a
`max-content minmax(0,1fr)` grid, so a long name or a long recipient list wraps
inside its own cell instead of pushing the timestamp off the pane.

Also corrected: measure `800px` → `68ch` (800px was ~110 characters per line against
a spec ceiling of ~80); body `--text-md` → `--text-base`; subject `700` → semibold;
sender/address sizes per §9.6; `MailWorkspace`'s `sr-only` `<h2>Mail</h2>` removed
because `WorkspaceHeader` already renders that view's `<h1>Mail</h1>` — a screen
reader was hearing "Mail" twice. The sender avatar was removed: §0 rejects fake
avatars, §8 allows an icon only where it carries meaning, and the name is already on
screen. It was also the only source of a raw `#ffffff` and two raw `rgba()` values.

### The finding that mattered most
**Every responsive rule for the reading pane had never once applied.**
`.mail-pane` (the list pane) is `container-name: mail-pane`, and four
`@container mail-pane` queries style `.reader-scroll`, `.reader-document`,
`.reader-subject` and `.toolbar-title`. But the reader is a **sibling** of the list
pane, not a descendant, so none of those rules ever matched. The reader had no
responsive behaviour at any width. They now sit in `@container mail-workspace`, whose
container element (`.mail-workspace`) does contain the reader. This is the same class
of defect as the UI-7 specificity bug: code that looks correct and does nothing.

### Undefined tokens
`--reader-border`, `--radius-xl` and `--highlight-top` are referenced 26 times across
the app and **defined in no stylesheet**, so every one of those declarations is
invalid at computed-value time. Six were in the reader: the surface had no border, no
radius and no shadow, there was no divider under the metadata, and the attachment tile
had no border — all quietly absent, not merely wrong. The reader's six are fixed.
**The other 20 sites are not** and are listed under remaining work.

### Honesty fix
`hasAttachments()` inferred attachments from `sizeEstimate > 250_000` and checked that
guess *before* the provider's `has_attachment` flag — but `sizeEstimate` is Gmail's
size for the **whole RFC822 message**, not its attachments. A large plain email was
therefore reported as "Attachment · 900 KB". The authoritative flag is now checked
first and the heuristic is only a fallback. The backend persists no per-file metadata,
so the pane shows a count only when one is actually supplied and never invents a
filename; it says "Attachments" rather than guessing. A per-file list needs a backend
data change, not a UI change.

### Also fixed
`.skeleton` was defined twice with different gradients and durations (the later block
won); a duplicate `.reader-body` rule; `.reader-scroll` padding of `28px 32px 44px`
(§2 names 28 and 44 as non-existent); `160px` and `380px` magic numbers; `9px`/`5px`
gaps and a literal `font-weight: 600` on `.toolbar-action`; `0.06em` tracking on a
caps label (§1 says `0.04em`); six inline `style` blocks in the loading skeleton.
A copy-acknowledgement timer is now cleared on message change, so selecting another
message could not leave "Copied" showing against the wrong email.

**43 new tests** cover short and very long subjects, long sender names, empty/single/
twelve recipients, long and short bodies, absent and unparseable timestamps, missing
display names, attachments with and without a flag or count, the narrow-width CSS
rules, and heading order. Nine of them assert against the **real stylesheets on disk**,
because a declaration naming an undefined token or a rule stranded in a dead
container query passes every DOM test and does nothing on screen. They would have
caught both defects above.

**Verification:** Rust 35, backend 239, tools 9, frontend 265 — **548 passed, 0
failed** (up from 505). `cargo fmt`, `clippy`, `tsc`, ESLint, production build (0
source maps) and the secret scan clean. Knowledge graph current.

---

## DEAD CSS GATE (DONE — commit `fix(alfred): resolve dead responsive and token CSS`)

Files: `styles/globals.css`, `styles/surfaces.css`, `styles/styles.test.ts` (new),
`docs/UI-DESIGN-SPEC.md`. CSS shrank 57.93 kB → 56.57 kB.

### The intelligence pane had exactly the reader's bug
`.intel-head` and `.intel-scroll` padding rules sat in `@container mail-pane
(max-width: 900px)`. The intelligence pane is a **sibling** of the list pane, so
that query could never match them — the rules had never applied. They now sit in
`@container mail-workspace`, whose container element contains them. The
`@container mail-pane` blocks now hold only list-pane selectors, and
`@container mail-workspace` holds only reader and intelligence selectors. The
1100px rail collapse is a window `@media` block and touches only shell/rail/header
selectors, so it cannot collide.

Design intent was preserved verbatim — the 900px intelligence rule is padding
compression, *not* the collapse-to-toggle of spec §13. That collapse was never
written; the old comment claiming otherwise was corrected.

### Four tokens, none of them defined — and none of them worth defining
| Token | Sites | Resolution |
| --- | --- | --- |
| `--highlight-top` | 18 | **Deleted.** A fake inset gloss. Spec §6 allows shadow for elevation only, never decoration. Every one of those declarations was invalid, so 18 elements were rendering with *no shadow at all*. Where the same declaration also held a valid token it was kept. |
| `--shadow-accent` | 3 | **Deleted.** Spec §6 and §15 removed it by name. |
| `--reader-border` | 2 | **Replaced with `--border-subtle`.** A separate "reader border" would duplicate it. |
| `--radius-xl` | 2 | **Replaced** with `--radius-lg` on the modal `.source-preview` and `--radius-md` on the `.intelligence-pane` panel. §4's scale is xs/sm/md/lg/full; §4 also says a panel is not a card. |

The sweep then found two more: `--bg-panel-solid` on `.startup-mark` (→ `--bg-panel`)
and `--danger-border` on `.analysis-progress-bar.tone-error` (→ `--danger`, dropping a
raw `rgba()` fallback). `--stagger` is **not** a defect: it is set inline by Overview
and Settings and carries a `0` fallback, which is the one legitimate use of an
undefined property.

### Six selectors were fighting themselves
Two generations of button and badge styling, with the older block's values silently
dead in every case: `.badge` (4), `.btn` (5), `.btn-danger`, `.btn-primary` (its
whole gradient background), `.btn-sm`, `.draft-panel`. Merged, with the later
value winning per property — provably render-neutral, and verified as such by
diffing effective computed declarations against HEAD. Also removed: an exact
duplicate `.reader-pane` block **introduced during UI-5**, and a cross-sheet
`.pane-separator:focus-visible` defined in both `surfaces.css` and `globals.css`
with conflicting values.

### Spec violations fixed along the way
`font-weight: 800` at 4 sites (spec §1 allows four steps) and 43 more weights
written as literals rather than tokens. Three coloured glows removed — the
`.status-dot` trio and `.deadline-dot` — because §6 says shadow is elevation,
never glow, and no coloured shadow. The 7 zero-blur `0 0 0 3px var(--accent-soft)`
rings were **kept**: those are focus indicators, which §5 and §11 require.

### The gate is a test, not a promise
`src/styles/styles.test.ts` (27 tests) reads the six real stylesheets from disk and
asserts: no property is referenced without a definition or a fallback; the retired
tokens stay retired; no raw hex outside the token layer; weights are tokens and
only the four steps exist; no tinted glow while focus rings survive; every
container name a query names is actually declared; no reader or intelligence rule
sits in a container that cannot reach it; no property is declared twice in one
rule; no identical selector is defined twice in flat scope; the reading measure
stays 68ch; the reader and intelligence text containers can wrap.

**It was mutation-tested.** Reintroducing each defect one at a time — the undefined
tokens, the intel rule moved back into `mail-pane`, a coloured glow, `font-weight:
800`, the duplicate `.reader-pane`, a deleted wrap guard, and a query naming a
container that does not exist — fails the suite in all seven cases. It is not a
string search.

### What this gate changed on screen
Fixing an invalid declaration restores the style that was always meant to be there,
so these are real visual changes: the intelligence pane, the draft panel and the
startup mark **gain** a border or background that was never rendering; the source
preview gains an 8px radius and the intelligence pane a 6px one; four small-caps
labels drop from 800 to 600; the status dots lose their coloured halo. None of it
can be confirmed without rendering the app.

**Verification:** Rust 35, backend 239, tools 9, frontend 292 — **575 passed, 0
failed** (up from 548). `cargo fmt`, `clippy`, `tsc`, ESLint, production build (0
source maps), secret scan and knowledge graph all clean.

---

## UI-8 ACCOUNTS + SETTINGS (DONE — commit `feat(alfred): productize accounts and settings UI`)

Files: `AccountsPage.tsx`, `SettingsPage.tsx`, `WorkspaceHeader.tsx`, `States.tsx`,
`styles/globals.css`, plus new `components/ui/Settings.tsx`, `lib/aiState.ts`,
`AccountsPage.states.test.tsx`, `SettingsPage.states.test.tsx`.

### Two real defects, not restyling
**Accounts had no error state at all.** A failed `/api/accounts` rendered
"No accounts connected" — the exact conflation UI-7 removed from four other pages,
still live in the fifth. It now has a distinct error branch with a real `refetch`
retry, and a test asserts the empty state never appears on failure.

**Settings fabricated the model.** The page hardcoded `qwen3:4b` while
`AnalysisStatus.model` reports what the supervisor is actually running. It now reads
the real field, shows `Unknown` before the first response, and a test fails if the
hardcoded string reappears. The status row also used the loose `health.ai` string
where the typed `AIState` machine exists; it now uses the real state.

### States are the backend's, not invented
The backend only ever writes `connection_status` of `connected` or `error`
(`gmail.py` sets `error` when the token refresh fails). There is no `disconnected`,
no `connecting`, no `auth_required` value — so none is shown. `error` is presented
as **Authentication required** with a **Reconnect** action, because that is what it
actually means and reconnect is an action the app really supports. An unrecognised
status is reported as reported rather than coerced into a healthy-looking row.

Backfill is surfaced read-only (`Complete` / `Importing · about N left` / `Paused` /
`Failed`), because the resume and pause controls already live in the mail pane and
duplicating them would be two places to keep in sync.

### One component layer, not a bespoke one per page
`SettingsSection`, `SettingsRow`, `SettingsValue` and `StatusIndicator` in
`components/ui/Settings.tsx`. `StatusIndicator` is the spec §3.5 requirement made
real: icon *and* label, so status survives greyscale and a screen reader. The old
`.status-dot`-plus-adjacent-text pattern is gone from both pages.

`lib/aiState.ts` is now the single description of the AI state machine, carrying a
chip label, a settings word, a hint, a sentence and a tone. It was previously
restated with **five** vocabularies; the header and Settings now share it and the
strings their tests pin are unchanged.

### Preserved deliberately
The OAuth flow is untouched: same `connectGmail(apiBase() + callback)` call, same
`window.open`, same `auth_success` message listener, same dynamic-port handling for
packaged Tauri. Both existing tests for that still pass. No token handling, no
origin validation and no credential storage was touched — UI-8 styles the current
OAuth state and nothing more. `analysisRetry` stays in `AnalysisProgress` alone
rather than gaining a second restart button in Settings.

### What was removed, and why
The account card's 38px accent-soft tile with a Mail glyph: spec §0 rejects fake
avatars and §8 allows an icon only where it carries meaning. The real identity is
the address, which is shown as text. A test asserts no avatar element and no
"score"/"health" copy exists.

~25 inline `style` objects across the two pages became classes. One real UI bug
surfaced while testing them: with no `display_name`, the address rendered **twice**
(name and detail). The detail line is now shown only when it adds something.

### CSS
New rules are intrinsically responsive — `flex-wrap` and `repeat(auto-fit, minmax())`
— deliberately **not** container queries, because these pages sit outside the mail
workspace and a pane-keyed query could never reach them. The style gate now asserts
that no `@container` block mentions settings or accounts, so that mistake cannot be
reintroduced silently. The account card dropped `--radius-lg` to `--radius-md` and
its `--shadow-1`: §4 says a panel is not a card, and §6 gives panels no shadow.

**39 new tests** (22 Accounts, 17 Settings) plus 5 new stylesheet guards. The style
guards were **mutation-tested**: dropping `min-width: 0`, un-wrapping a row, turning
`auto-fit` into a fixed count, deleting a tone, and substituting a literal for a
spacing token are each caught.

One gap the mutation pass exposed and I closed: the off-scale check had been lost
when the stylesheet suite was rewritten in the dead-CSS gate, so a `2px` gap slipped
in. It now also rejects *on-scale literals*, because `padding: 20px` is as much a
one-off as `padding: 22px`.

**Verification:** Rust 35, backend 239, tools 9, frontend 337 — **620 passed, 0
failed** (up from 575). `cargo fmt`, `clippy`, `tsc`, ESLint, production build (0
source maps), secret scan and knowledge graph all clean.

---

## UI-10 FOCUS MOVEMENT (DONE — commit `feat(alfred): complete keyboard focus management`)

Files: new `lib/focus.ts`, `App.tsx`, `WorkspaceHeader.tsx`, `MessageReader.tsx`,
`MessageList.tsx`, `MessageRow.tsx`, `MailWorkspace.tsx`, and the four pages that
own a retry. New tests: `layout/focus.test.tsx`, `mail/MailWorkspace.focus.test.tsx`,
`features/focus.retention.test.tsx`, `features/focus.retry.test.tsx`.

### The rule, made structural rather than remembered
Focus intent is **recorded by whatever replaces the user's context and consumed
once**. Nothing infers it from a state change, which is what makes "a background
refetch never moves focus" true by construction instead of by discipline. Two bugs
found during the audit came from the obvious alternative — an effect keyed on
`page` — and both were fixed by recording intent instead.

### Defects found and fixed
**Message activation never moved focus at all.** Selecting a message updated the
reader silently; the user's focus stayed wherever it was. The reader subject is now
focusable (`tabIndex={-1}`, so no new tab stop) and keyboard activation of a row —
Enter or Space, not a click — moves focus to it, so the message is announced.
Pointer activation deliberately does not: the cursor is already where the user is
looking.

**A successful retry stranded focus on `<body>`.** The "Try again" button lives
*inside* the error block, so a successful retry unmounts the element that had
focus. `useRetryPreservingFocus` awaits the refetch and re-homes focus to the view
heading **only when the retry actually worked** — on a persistent failure the
error and its button are still the right place to be, and a test pins that.

**Escape in the search field dropped focus on the floor.** It called `blur()` and
stopped, leaving the user on `<body>`. It now records where focus came from before
`Ctrl+K` and hands it back, guarded on the element still being connected.

**Cross-page "Open in Mail" lost focus entirely.** The Tasks or Deadlines button
the user pressed unmounts on navigation, so focus fell to `<body>`. It now records
reader intent.

### Two judgement calls, both deliberate and tested
**The sidebar does not get focus moved on navigation.** Arrowing the rail both
moves focus *and* changes the page, so honouring intent there would pull the user
out of the rail on the first arrow press and break arrow navigation outright. Rail
activation keeps focus on the item; a test asserts it. **Typing a global search
does not move focus either**, even though it changes page — the user's focus is in
the search field and taking it away mid-keystroke would be hostile. That case is
the reason intent is explicit rather than derived from `page`.

**The skip link now moves focus explicitly.** The `href` is kept so it works with
scripting off; the explicit focus makes the behaviour deterministic instead of
depending on fragment navigation, which jsdom does not perform. The target was
already `tabIndex={-1}`.

### Found, reported, not fixed
`MessageList` is `role="listbox"` whose rows are `role="button"`: no arrow-key
handling, no `aria-activedescendant`, and every row is a tab stop, so tabbing
through a large mailbox is unusable. Spec §11.5 wants options in a single tab
stop. That is an interaction-model change rather than focus movement, so it is
recorded as the top remaining item. It is also the honest limitation of the reader
focus: because the list has no arrow keys, focusing the reader on Enter leaves
Shift+Tab as the route back, and proper listbox semantics would make that moot.

Five views render **two `h1`s** (their own plus the header's). Focus targets the
header heading because it is the unambiguous one; the duplication is recorded.

A static guard asserting every `.focus()` sits in an effect or a handler was
written and **deliberately not shipped** — it flagged the dialog focus trap, which
is correct code inside a long keydown listener. A guard with false positives
trains people to ignore it. The `autoFocus` check shipped; the behavioural tests
are the real evidence.

**37 new focus tests**, all asserting `document.activeElement` rather than
presence: sidebar single-tab-stop and arrow/Home/End, activation keeping focus,
keyboard vs pointer activation, second-message activation, intent consumed exactly
once, a re-render that must not steal focus, re-activating the same message,
`Ctrl+K`, typing, Escape returning focus, theme control, retry recovery, retry
failure leaving focus put, and a failing refetch arriving under the user.

**Verification:** Rust 35, backend 239, tools 9, frontend 374 — **657 passed, 0
failed** (up from 620). `cargo fmt`, `clippy`, `tsc`, ESLint, production build (0
source maps), secret scan and knowledge graph all clean. Static review confirmed
no `autoFocus` anywhere, and every `useEffect` has a dependency array.

---

## REMAINING WORK

**UI (this phase):**
1. **The message list is not keyboard navigable.** `MessageList` is
   `role="listbox"` but its rows are `role="button"`, there is no arrow-key
   handling, and every row is its own tab stop. Spec §11.5 wants a listbox of
   options with a single tab stop. This is an interaction-model change, not focus
   movement, so it was left alone — but it is why focusing the reader on Enter
   leaves no arrow-key route to the next message.
2. Four AI-state vocabularies (rail, intelligence panel, progress bar, and the
   header's own consumers) still restate the state machine. `src/lib/aiState.ts`
   is the single source; fold them in.
3. Three pre-existing off-scale values survive in the intelligence panel
   (`.intel-kv` and `.intel-item` at `6px 0`, and a `3px` optical nudge on
   `.intel-item svg`). Deliberately left: correcting them moves pixels in a pane
   that has never been rendered, so it belongs with the visual pass.
4. `.section-label` uses `font-size: 10px` and `letter-spacing: 0.09em`; the spec
   scale is `--text-2xs` (10.5px) and `0.04em` for caps. It is shared with pages
   outside this phase, so it was not changed here.
5. `.status-dot.online` pulses on a 3.2 s infinite loop. Spec §7 does not list a
   looping status pulse as animatable, and it never stops. UI-11 decision.
6. `.badge-reply` is coloured with `--accent-soft` / `--accent-text`. Spec §3.3
   reserves accent for selected, focused, unread and primary action — "nothing
   else". A reply-needed badge is arguably none of those. Needs a call.
7. Four `#f28b82` values survive as `var(--danger, #f28b82)` fallbacks. They never
   paint, so they are harmless, but spec §3 says components never name a raw hex.
8. Every non-rail view renders its own `<h1>` while `WorkspaceHeader` also renders
   one, so those five views have two `h1`s. Focus targets the header heading
   precisely because it is unambiguous; the duplicate is recorded, not fixed.
9. Remaining inline `style` objects on pages other than Accounts and Settings.
10. `Ctrl+1..6` navigation shortcuts and a `?` shortcut overlay (spec §12).
11. Real brand asset set — still placeholders (F8).
12. Accounts: OAuth popup → system browser, `event.origin` check (F13, F14) — Phase 2.

**Not started (later phases):** first-run model setup (Phase 2), website (Phase 6),
installer signing and CI (Phases 5, 7).

**Verification still owed for Gate 1:** the packaged-app manual launch. F1 is fixed in
code and statically asserted, but "one launch shows the window" has not been observed on
a real install. `docs/Phases.md` Gate 1 requires that manual pass with `desktop.log`
attached and a `tasklist` check after quit.

---

## GATE STATUS

**Gate 0: PASS** (unchanged).

**Phase 1: PARTIAL — not declared PASS.** Priorities 1–6 are complete with test
evidence, and the UI steps UI-1 through UI-11 are now all done with test evidence.
What is missing is the one thing no test can supply: someone has to look at the
running app. Items 1–12 above remain, and Gate 1 cannot be declared PASS until the
packaged-app manual launch is observed. The directive states explicitly: do not
claim the phase is complete if only the foundation is done.

---

## NEXT TASK

**Phase 1 visual verification, then UI cleanup.** Every automated gate is now
closed; what is missing is someone looking at the thing. Five commits' worth of
change has never been rendered: restored borders and backgrounds from the dead-CSS
gate, the new reading-pane hierarchy, the productised Accounts and Settings, and
the focus work.

**Manual visual verification NOT PERFORMED.** This environment cannot render Alfred.

The pass should cover, at minimum:

1. Launch the app; confirm the window appears (this is also **Gate 1**, still
   NOT PERFORMED — attach `desktop.log` and a `tasklist` check after quit).
2. Overview, Mail, Tasks, Deadlines, Accounts, Settings in **both themes**.
3. The reading pane with a short subject, a very long one, a long sender, many
   recipients, a long body, and attachments.
4. Resize through 1280 / 1100 / 1000 / 900 / 800px and look for horizontal
   overflow, a cramped reader, and the intelligence pane at 900px.
5. Keyboard only: `Tab` from the top, the skip link, `Ctrl+K` then `Escape`,
   arrow the sidebar, `Enter` a message and confirm focus lands on the subject,
   `Shift+Tab` back.
6. Error and empty states on all four pages, with a deliberately failing backend.

Two things to watch that no test can catch: the account card lost its avatar tile
and gained a fact grid, and Settings swapped a hardcoded model for a real one.

**Gate 1 packaged-app verification: NOT PERFORMED.**
**Automated verification status: PASS** (657 tests, 0 failures).
