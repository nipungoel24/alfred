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
| UI-5 reading pane | partial | `sr-only` h1 added to the Mail view; full hierarchy pass is remaining work |
| UI-6 intelligence | done | every section conditional; real empty states; no invented output |
| UI-7 states | done | all 4 pages distinguish loading / empty / success / failure; real `refetch()` retry; 33 new tests |
| UI-8 accounts/settings | not done | remaining |
| UI-9 responsive | done | 1100px collapse to icon rail implemented; 900px intelligence collapse remaining |
| UI-10 accessibility | partial | skip link, `sr-only`, h1 on Mail, landmarks, roving tabindex done; focus movement on navigation remaining |
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

## REMAINING WORK

**UI (this phase):**
1. Reading-pane hierarchy pass (UI-5): subject/sender/recipients/date/actions/body order
   and the 68ch measure.
2. Accounts + Settings onto the shared primitives (UI-8): four buttons with no
   `aria-label`, and a duplicated AI-label map.
3. Focus movement on page change and message selection (UI-10).
4. Replace the 31 inline `style` objects with tokens.
5. 900px intelligence-pane collapse (UI-9).
6. `Ctrl+1..6` navigation shortcuts and a `?` shortcut overlay (spec §12).
7. Real brand asset set — still placeholders (F8).
8. Accounts: OAuth popup → system browser, `event.origin` check (F13, F14) — Phase 2.

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
evidence. UI foundation is substantially complete; UI-7 (error vs empty) is now done and
items 1–8 above remain. The directive states explicitly: do not claim the phase is
complete if only the foundation is done. Gate 1 cannot be declared PASS until the
packaged-app manual launch is observed.

---

## NEXT TASK

Reading-pane hierarchy pass (UI-5) on the Mail view: subject, sender, recipients, date,
actions, then body, and enforce the 68ch measure. Verify at 1440×900 and 1280×800 in
both themes, and confirm the existing `sr-only` h1 still names the view.

Note for whoever picks this up: **UI-7 still owes a real visual pass.** The four error
branches are covered by jsdom tests only — nobody has looked at them rendered. Launch
the app with a backend that fails deliberately (stop `alfred-backend` while the UI is
open, or point it at a dead port) and check each page in light and dark, plus Tab order
onto the retry control.
