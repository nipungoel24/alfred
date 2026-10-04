# Alfred — Phases and Gates

Status: active
Baseline: Gate 0 complete, 2026-09-26

Work only on the active phase. Do not start the next phase until the current gate is
`PASS`. A gate that fails is reported as `FAIL` with the reason, not quietly skipped.

---

## Phase model

| Phase | Name | Gate | Depends on |
| --- | --- | --- | --- |
| 0 | Repository baseline | **Gate 0** | — |
| 1 | Startup and process lifecycle | Gate 1 | Gate 0 |
| 2 | First run and local AI setup | Gate 2 | Gate 1 |
| 3 | UX, design system, accessibility | Gate 3 | Gate 2 |
| 4 | Performance | Gate 4 | Gate 3 |
| 5 | Security | Gate 5 | Gate 4 |
| 6 | Public website | Gate 6 | Gate 3 (needs real screenshots) |
| 7 | Distribution | Gate 7 | Gates 1, 5 |
| 8 | Release | Gate 8 | All preceding |

Phase 6 is the only phase that may run partly in parallel with 4 and 5, because it needs
real product screenshots that only exist once the app launches correctly.

---

## Gate 0 — Repository baseline (COMPLETE, PASS)

**Purpose:** establish what exists before changing anything.

Required evidence, all produced:

| Item | Where |
| --- | --- |
| Source map with ACTIVE/LEGACY/TEST/GENERATED/BUILD/DOCUMENTATION/UNKNOWN classification | `docs/Memory.md` §Repository map |
| Architecture of all four layers | `docs/Architecture.md` |
| Dependency graph | `docs/Architecture.md` §21 |
| Startup path, both layers | `docs/Architecture.md` §4, §5 |
| Packaging path | `docs/Architecture.md` §16 |
| Test baseline, executed | `docs/Memory.md` §Evidence |
| Known issues, 40 numbered | `docs/Memory.md` §Findings |
| Product definition and non-goals | `docs/PRD.md` |
| Mandatory rules | `docs/Rules.md` |
| Design system with measured contrast | `docs/Design.md` |
| Decisions | `docs/decisions/ADR-001..007` |

**Status: PASS.** Every mandatory item has a document and the test baseline was executed,
not assumed.

---

## Gate 1 — Startup and process lifecycle

**Phase 1 goal:** one launch produces one visible window, a supervised backend, a
branded loading experience, and a clean exit. This is release-blocking and is first
because nothing else can be verified until Alfred actually appears on screen.

### Scope

| # | Item | Finding | Files |
| --- | --- | --- | --- |
| 1.1 | Show the window on a successful backend handshake | D1 | `desktop/src-tauri/src/main.rs`, `tauri.conf.json` |
| 1.2 | Replace the 3-state machine with the 11 named phases | D7 | `main.rs:55-105`, `StartupGate.tsx` |
| 1.3 | Named failure codes replacing prose reasons | D7 | `main.rs`, `StartupGate.tsx` |
| 1.4 | CSPRNG session token | D3 | `main.rs:224-240` |
| 1.5 | Constant-time token comparison | D16 | `backend/app/main.py:566` |
| 1.6 | Fix shutdown orphaning (`try_lock`) | D2 | `main.rs:507-515` |
| 1.7 | Fix stale poll-task race on restart | D4 | `main.rs:440-441` |
| 1.8 | Make `restart_backend` do something while `Starting` | D6 | `main.rs:437-439` |
| 1.9 | Real HTTP status parsing for health | D5 | `main.rs:318` |
| 1.10 | Install a logger so sidecar output is captured | D8 | `main.rs:105,108` |
| 1.11 | Branded splash + real startup UI states | §11 | `StartupGate.tsx`, `main.rs` |
| 1.12 | Bounded retry with cancellation in the gate | D10 | `StartupGate.tsx` |
| 1.13 | Rotate the shell log; add severity and correlation id | §14 | `main.rs:193-214` |
| 1.14 | Surface migration failure distinctly from health timeout | F25 | `main.py:41`, `main.rs:174` |
| 1.15 | Remove `localhost:5173` from the production CSP | D12 | `tauri.conf.json:25` |
| 1.16 | Rust tests that actually exercise the supervisor | D24 | `main.rs:520-809` |

### Mandatory acceptance criteria

- [ ] A single launch from the Start Menu produces exactly one visible window
- [ ] A second launch focuses the existing window and starts no second backend
- [ ] Zero console windows in a release build
- [ ] Splash/branded loading UI is visible from first paint
- [ ] Backend reaches `Ready` and the window is shown
- [ ] Every startup phase is represented and reachable: `BOOT`, `INITIALIZING`,
      `STARTING_BACKEND`, `WAITING_FOR_BACKEND`, `CHECKING_DATABASE`,
      `CHECKING_AI_RUNTIME`, `CHECKING_MODEL`, `RESTORING_SESSION`, `READY`,
      `RECOVERY`, `FATAL_ERROR` (11 phases; authoritative list is the
      `StartupPhase` enum in `desktop/src-tauri/src/main.rs`, mirrored by
      `STARTUP_PHASES` in `frontend/src/api/client.ts` and asserted by
      `startup_phases_serialise_as_documented`). `READY` and `RECOVERY` both
      release the workspace; `FATAL_ERROR` never does.
- [ ] A forced health timeout shows a named code, the log path, and a working Retry
- [ ] Retry is bounded and cancellable; no infinite polling
- [ ] A forced backend crash is detected and surfaced
- [ ] Quit leaves zero `alfred-backend.exe` processes, verified by `tasklist` after quit
- [ ] The runtime token is 256 bits from a CSPRNG
- [ ] `cargo fmt --check`, `cargo clippy --all-targets`, `cargo test` all pass
- [ ] `cargo test` includes at least one test that drives `BackendSupervisor`
- [ ] Rust tests stop referencing the nonexistent `SIDECAR_EXITED` state
- [ ] Production CSP contains no development origin
- [ ] The full existing suite still passes: 207 backend, 133 frontend, 9 tools

### Evidence required
Manual run of the packaged app with `desktop.log` attached; `tasklist` output before and
after quit; a screenshot of the splash; the new Rust test names and their assertions.

---

## Gate 2 — First run and local AI setup

**Phase 2 goal:** a user on a clean Windows machine with no Ollama and no model reaches a
working mailbox, guided rather than instructed.

### Scope

| # | Item | Finding | Files |
| --- | --- | --- | --- |
| 2.1 | First-run checklist UI | §7 | new `frontend/src/features/onboarding/` |
| 2.2 | Ollama installed / running detection surfaced | partial | `ai/supervisor.py` |
| 2.3 | Model presence check with a real state machine | partial | `ai/supervisor.py` |
| 2.4 | Model pull with real progress, size, cancel, resume | NOT BUILT | new |
| 2.5 | Disk-space check before download | NOT BUILT | new |
| 2.6 | System-resource check | NOT BUILT | new |
| 2.7 | Model selection in Settings | NOT BUILT | `SettingsPage.tsx` |
| 2.8 | System browser for OAuth consent | D18 | `AccountsPage.tsx:22` |
| 2.9 | `event.origin` check on the OAuth message | D17 | `AccountsPage.tsx:41-45` |
| 2.10 | Denied / cancelled / expired-revoked consent states | §8 | `AccountsPage.tsx` |
| 2.11 | Disconnect and reconnect with clear connected-account identity | §8 | `AccountsPage.tsx` |
| 2.12 | `OAUTH_STATES` expiry and bound | D15 | `main.py:47` |

Model states required, as a real state machine and not as prose:
`MODEL_RUNTIME_MISSING`, `MODEL_RUNTIME_STARTING`, `MODEL_DOWNLOAD_REQUIRED`,
`MODEL_DOWNLOADING`, `MODEL_READY`, `MODEL_FAILED`.

**Download progress must be real.** Ollama's `/api/pull` streams newline-delimited
JSON with per-layer `completed`/`total` byte counts. Progress is computed from those
bytes, never simulated. A fake progress bar is a release blocker.

### Mandatory acceptance criteria

- [ ] On a machine with no Ollama, the first-run screen appears and explains the next step
- [ ] On a machine with Ollama stopped, Alfred offers to start it and does
- [ ] With Ollama running and no model, the real required size is shown
- [ ] Download progress matches actual bytes pulled, verified against `ollama list`
- [ ] Download can be cancelled and leaves no corrupt model
- [ ] An interrupted download resumes or restarts cleanly
- [ ] Insufficient disk space is detected before the download starts
- [ ] The model is selectable in Settings and the change is applied without a restart
- [ ] OAuth consent opens in the system browser
- [ ] Denied consent shows a real message and leaves Alfred usable
- [ ] A revoked refresh token surfaces reconnect, not a silent failure
- [ ] The connected account is visibly identified with disconnect available
- [ ] `OAUTH_STATES` cannot grow without bound
- [ ] Full existing suite still passes

---

## Gate 3 — UX, design system, accessibility

**Phase 3 goal:** the interface is coherent, accessible, and free of decoration that
does not earn its place.

### Scope
- Implement `docs/Design.md`: token corrections, orb removal, glass reduction
- Remove the Tailwind preflight and the four unused Tailwind-family dependencies
- Resolve the shadcn `components.json` half-commitment (ADR-004)
- Skip-to-content; `<h1>` on every page including Mail
- Focus movement on page change and message selection
- `aria-describedby` / `aria-labelledby` / `aria-expanded` / `aria-controls` where needed
- `ThemeToggle` keyboard correctness
- Live-region announcements for AI and sync state
- `Ctrl K` affordance made Windows-specific
- Remove the ambient orb layer and its `App.tsx` markup
- Fix the React setState-during-render warning (F20)
- Fix or delete the four vacuous frontend tests (F21)
- Remove dead code: `lib/utils.ts`, empty `features/email/`, empty `features/inbox/`,
  empty `backend/app/api/`, `WORKER_CONCURRENCY`, `BACKFILL_CURSOR_FIELDS`,
  `SYSTEM_LABELS`, `PROMPT_VERSION`, unused API client exports
- Reconcile or delete `frontend/DESIGN.md`
- Fix the broken `/icon-192.png` reference (F10)
- Keyboard shortcut system, documented and discoverable
- Narrow-width audit at 900px in both themes

### Mandatory acceptance criteria

- [ ] Every token in `docs/Design.md` §3.2 measured and passing in both themes
- [ ] Zero text usages of `--text-faint`
- [ ] Zero ambient orbs; zero decorative motion loops
- [ ] Every page has exactly one `<h1>`
- [ ] Skip-to-content is the first tab stop and moves focus to `<main>`
- [ ] The whole application is operable by keyboard alone, with a recorded pass
- [ ] `prefers-reduced-motion: reduce` produces no motion
- [ ] No horizontal overflow at 900px width, either theme, any page
- [ ] Zero console errors or warnings in a production build
- [ ] No test in the suite that cannot fail
- [ ] No unused dependency or dead source file remains
- [ ] No broken asset reference
- [ ] Every navigation item reaches a real, working view
- [ ] All keyboard shortcuts documented and discoverable in-product
- [ ] Full existing suite still passes, and the four vacuous tests are gone

---

## Gate 4 — Performance

**Phase 4 goal:** measured improvement, with before/after evidence for every change.

### Baseline recorded at Gate 0

| Metric | Value | How measured |
| --- | --- | --- |
| JS bundle | 375.83 kB raw / 113.98 kB gzip, **single chunk** | `vite build` |
| CSS bundle | 63.87 kB raw / 11.87 kB gzip | `vite build` |
| Stylesheet | 2 567 lines, 366 rule blocks, 69 475 B in one file | `frontend/src/styles/globals.css` |
| Fonts shipped | 0 bytes (system stack) | no `.woff`/`.ttf` tracked |
| Source maps in `dist` | 0 | `Get-ChildItem dist -Filter *.map` |
| Largest component | `MailWorkspace.tsx`, 629 lines, 12 `useState`, 6 `useMemo` | — |
| Backend startup | **not yet measured** | requires Gate 1 working build |
| Model initialisation | **not yet measured** | requires Ollama |
| Cold launch to READY | **not measurable today** | D1: the window never appears |

Startup timing is unmeasurable until Gate 1 is fixed. That is the correct order.

### Scope
- Route-level or pane-level code splitting; the 375 kB single chunk is the target
- Split `globals.css` by concern so a change does not invalidate the whole sheet
- Reduce `MailWorkspace` render cost: virtualisation, stable callbacks, narrower state
- Fix the ineffective dynamic import of `api/client.ts` (it is statically imported too)
- Measure and record: cold launch → READY, backend spawn → healthy, model load, memory

### Mandatory acceptance criteria

- [ ] Startup time measured and recorded, with the method stated
- [ ] Bundle split by route or pane; no single chunk above 200 kB raw
- [ ] No duplicated dependency in the bundle graph
- [ ] Mail list rendering measured with 5 000 messages; virtualised if it is not smooth
- [ ] Memory measured at idle and after a 5 000-message sync
- [ ] Every optimisation has a before/after number
- [ ] No optimisation shipped without evidence

---

## Gate 5 — Security

**Phase 5 goal:** every control in `docs/Architecture.md` §20 is either correct or
explicitly accepted with a reason.

### Scope

| # | Item | Finding |
| --- | --- | --- |
| 5.1 | Stop shipping the OAuth client secret in the binary | D13 |
| 5.2 | Move to PKCE-only, secret-free Desktop-app auth, or document the residual risk | D13 |
| 5.3 | DPAPI failure must be loud, never a base64 downgrade | D14 |
| 5.4 | CSPRNG session token (from Gate 1) | D3 |
| 5.5 | Constant-time token comparison (from Gate 1) | D16 |
| 5.6 | `event.origin` verification (from Gate 2) | D17 |
| 5.7 | Production CSP without dev origins (from Gate 1) | D12 |
| 5.8 | `OAUTH_STATES` bound (from Gate 2) | D15 |
| 5.9 | Version-tag stored tokens so DPAPI and base64 are distinguishable | D14 |
| 5.10 | Fix `get_auth_url` percent-encoding | F22 |
| 5.11 | Uniform API error envelope | F23 |
| 5.12 | Remove broad `except Exception: pass` from `app/` | §1.16 |
| 5.13 | Remove the `print()` in the migration path | F24 |
| 5.14 | Move raw SQL out of `main.py` into the repository | F24 |
| 5.15 | `/docs` and `/openapi.json` gated in a packaged build | §4 |
| 5.16 | `ALLOWDOWNGRADES` decision | D36 |
| 5.17 | WebView2 offline installer decision | D36 |
| 5.18 | Verify no secret appears in any log | §14 |
| 5.19 | Tauri capability review — confirm least privilege still holds | §20 |

### Mandatory acceptance criteria

- [ ] `strings` over the shipped sidecar reveals no OAuth client secret
- [ ] A forced DPAPI failure produces a loud error, not a silent downgrade
- [ ] Stored credentials carry a format version tag
- [ ] Session token is CSPRNG-generated and compared in constant time
- [ ] A postMessage from an unexpected origin is rejected
- [ ] Production CSP contains no `localhost` or dev origin
- [ ] `/docs` and `/openapi.json` are unreachable in a packaged build
- [ ] Zero bare `except Exception: pass` in `backend/app/`
- [ ] Every error response uses one envelope shape
- [ ] No log line in any run contains a token, credential, or message body
- [ ] Capability set is minimal and every grant has a stated need
- [ ] Rotate the OAuth credentials currently sitting in `build/sidecar-config/`,
      `desktop/src-tauri/binaries/`, and the root `.env`, and in the 39 MB built sidecar
- [ ] Full existing suite still passes

---

## Gate 6 — Public website

Nothing exists today. Verified: no site framework config, no site directory, no tracked
YAML, and the only frontend is the application.

### Decision required first
A static site needs a home. Options: a `website/` workspace in this repository, or a
separate repository. **Recommendation: a separate repository.** The application
repository should not carry a marketing site, its analytics, its build, and its
deployment. This needs an owner decision before work starts, and Phase 6 does not begin
until it is made.

### Page policy
The list below is a **ceiling, not a quota.** A page ships only with real content.

| Page | Content requirement |
| --- | --- |
| `/` | What Alfred actually does. Real screenshot. No invented metrics. |
| `/features` | Feature-by-feature, each tied to a real capability |
| `/how-it-works` | Architecture and data flow, honestly described |
| `/security` | The privacy model from `docs/PRD.md` §11, including the DPAPI caveat |
| `/docs` | Link into the real documentation |
| `/download` | Only platforms with an actual built and tested release |
| `/faq` | Real questions, real answers |
| `/changelog` | From `CHANGELOG.md` |
| `/contact` | A real, monitored channel |
| `/privacy` | `docs/PRD.md` §11 expanded; no invented legal claims |
| `/terms` | Same constraint |
| `/thank-you` | Form destination |
| `/404` | Real 404 |
| `/case-studies` | **BLOCKED** — requires real customers. Ship an honest pre-release page or omit the route. |
| `/sitemap.xml` | Only real canonical URLs |
| `/robots.txt`, `/llms.txt`, `/favicon.ico` | — |

### Mandatory acceptance criteria

- [ ] Unique title, description, and canonical URL on every page
- [ ] Exactly one `<h1>` per page; logical heading order
- [ ] Open Graph and Twitter metadata with a real product image per key page
- [ ] Structured data validates and contains no fabricated ratings, reviews, locations,
      or counts
- [ ] Sitemap contains only real canonical URLs
- [ ] `robots.txt`, `sitemap.xml`, `llms.txt`, `favicon.ico` all resolve
- [ ] Every internal link resolves; zero placeholder links
- [ ] Custom 404 returns a real 404 status
- [ ] Mobile and desktop verified at 360, 768, 1280, 1920
- [ ] Light and dark verified
- [ ] Zero console errors, zero failed requests, zero missing images
- [ ] Every meaningful image has real alt text
- [ ] Google Analytics on the website only, consent-gated, and provably absent from the
      application bundle
- [ ] No fake reviews, testimonials, counters, or customer photography anywhere
- [ ] No `localhost`, `Vite`, or `React` in any title

---

## Gate 7 — Distribution

### Scope
- CI that builds the installer from source on a clean runner
- Publisher metadata; `MANUFACTURER` is currently the literal `alfred`
- Real brand assets in the installer, taskbar, and Start Menu
- Authenticode signing, or an explicit, documented decision not to sign
- MSI if it is genuinely wanted; NSIS alone is acceptable if documented
- Checksum publication
- Install, upgrade, downgrade decision, uninstall, and reinstall verified on a clean
  machine
- `verify_windows_install.ps1` extended: it currently prints process status but has no
  check for it, and no orphan-process assertion

### Mandatory acceptance criteria

- [ ] A clean runner produces a working installer with no local machine state
- [ ] Publisher, homepage, description, and icon are populated
- [ ] App icon, taskbar icon, Start Menu icon, and installer icon are the real brand asset
- [ ] Install → launch → quit → uninstall leaves no files, shortcuts, or processes
- [ ] Reinstall over an existing install works
- [ ] Upgrade from the previous version preserves user data
- [ ] Checksums published alongside artifacts
- [ ] Release manifest version read from a single source, not hardcoded
- [ ] No development dependency in the shipped tree
- [ ] No source maps in any shipped artifact
- [ ] Uninstall verified on a clean Windows profile

---

## Gate 8 — Release

No known release-blocking issue. No:

- console errors
- terminal windows
- placeholder branding
- fake content
- broken links
- broken installer
- source-map exposure
- failing mandatory tests
- unhandled startup race

Plus every acceptance criterion in `docs/PRD.md` §16 evidenced, and `README.md` describing
the artifact that actually exists.

---

## Freeze policy

When a phase declares files frozen, they are not modified without written justification
that records: why, the exact change, the tests re-run, and the gate audit update.

Phase 1 freezes: `backend/app/db/database.py`, `backend/app/db/repositories.py`,
`backend/app/mail/eligibility.py`, and all of `backend/tests/`. The startup work must not
disturb the data layer or the test suite. An emergency change to a frozen file requires
the four steps above in the gate report.
