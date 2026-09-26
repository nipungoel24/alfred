# Alfred — Product Requirements

Status: active
Baseline established: Gate 0, 2026-09-26
Repository state at time of writing: branch `feature/mail-workspace-productization-20260907`, HEAD `3cea34f`

Every claim in this document is traceable to code, a running command, or an ADR.
Anything not yet true is written in the future tense and marked **NOT YET BUILT**.

---

## 1. Product purpose

Alfred is a local-first Windows desktop application that keeps a private mirror of a
Gmail mailbox on the user's own machine and runs a local language model over it to
answer three questions:

1. What needs my attention?
2. What did I promise to do, and by when?
3. What did somebody actually say?

Alfred is not a mail client. It does not send, modify, delete, or mark mail. It is a
read-only intelligence layer over a mailbox you already own.

## 2. Target users

Stated as roles the product is designed for, not as market segments. Alfred is
Windows-only, Gmail-only, and requires the user to be comfortable running a local
model.

| Role | Why Alfred fits |
| --- | --- |
| Individual knowledge worker on Windows | Wants a daily briefing without opening Gmail. Accepts installing Ollama. |
| Privacy-sensitive professional | Needs mail triaged without handing content to a cloud AI vendor. |
| Technical evaluator | Wants to read the source, run it locally, and verify the privacy claims. |

Explicitly not a target: non-Windows platforms, non-Gmail providers, organisations
requiring Google Workspace admin controls, shared/multi-user machines, and anyone
requiring a compliance certification. See §13 Non-goals.

## 3. User problems

Each problem below is one the current code demonstrably addresses.

| # | Problem | Current implementation |
| --- | --- | --- |
| P1 | Inbox triage is manual and inconsistent | `backend/app/mail/eligibility.py` classification, `backend/app/ai/service.py` analysis, Overview briefing |
| P2 | Commitments buried in mail threads are missed | `backend/app/services/task_derivation.py` derives tasks + deadlines, `frontend/src/features/tasks/TasksPage.tsx` |
| P3 | Search in a large mailbox is slow and imprecise | SQLite FTS5 + BM25, `backend/app/db/repositories.py:369` |
| P4 | AI output cannot be trusted without the source | `frontend/src/mail/SourceEmailPreview.tsx` opens the exact source message |
| P5 | False positives destroy trust in AI output | Durable dismissal, `backend/app/db/repositories.py:861` |
| P6 | Mail content must not leave the machine | Ollama-only, no cloud AI fallback, `backend/app/ai/ollama_client.py` |
| P7 | Mail tokens must be protected at rest | Windows DPAPI, `backend/app/db/secure_store.py` |
| P8 | A large mailbox cannot be synced in one blocking pass | Durable backfill job, `backend/app/mail/backfill.py` |

## 4. Product principles

1. **Local-first, not local-only.** Mail sync talks to Google. AI inference does not
   leave the machine. The product must be honest about which is which.
2. **Show the source.** Every AI-derived claim links to the message it came from.
3. **AI can be wrong, and the UI says so.** Corrections are first-class, not hidden.
4. **Degrade, never block.** Ollama being down must not make the mailbox unusable.
5. **One process, one window, one launch.** The user never runs Alfred twice.
6. **Read-only.** Alfred never writes to Gmail. This is a scope boundary, not a phase.
7. **No invented telemetry.** Alfred has no analytics. Ever.

## 5. Primary workflows

### W1 — First run
Detect Ollama → detect or install the model → connect Gmail via system browser →
initial Inbox sync → background All Mail backfill → background analysis queue →
workspace ready. Current state: steps 3-7 exist; **steps 1-2 are NOT YET BUILT**
(see `docs/Phases.md` Phase 2).

### W2 — Daily briefing
Open Alfred → Overview → read the generated briefing → act on attention items →
open the source email for anything surprising. Exists.

### W3 — Triage the inbox
Mail → Gmail category tabs → read → mark Later → archive. Exists.

### W4 — Search
`Ctrl+K` → typed query with operators (`from:`, `subject:`, `is:`, `in:`, `has:`,
`after:`, `before:`, `category:`) → local FTS5 results. Exists.
Parser: `frontend/src/search/searchParser.ts`.

### W5 — Correct the AI
Tasks → open source preview → mark **Not a task** or override priority → the
correction survives re-derivation. Exists.

### W6 — Recover from a bad state
Failure screen → read diagnostic code → open the log file → Retry. Partially exists;
see F7 in `docs/Memory.md`.

## 6. Desktop features

Verified present in the working tree:

- Mail workspace with resizable Mail / Reader / Intelligence panes, layout persisted
  (`frontend/src/mail/MailWorkspace.tsx`, `frontend/src/mail/layoutStore.ts`)
- Inbox and All Mail scopes; All Mail kind filters for Sent and Archived
- Gmail category tabs (Primary, Social, Promotions, Updates, Forums) with live counts
- Structured local search over the mirrored mailbox
- Tasks and Deadlines pages with source-message preview
- Multi-account support with an account selector
- Background All Mail backfill with progress, pause, retry
- Local AI status surfaced in the rail and header
- Light and dark themes, including system-following
- Configurable pane layout, validated and versioned
- Task priority override and durable task dismissal

## 7. Onboarding

**NOT YET BUILT.** Today a first-run user must independently install Ollama, pull a
model, and create their own Google OAuth Desktop client. This is documented in
`README.md` but is a manual procedure, not product onboarding. Required: a first-run
checklist that detects runtime state and walks the user through what is missing.

## 8. Gmail integration

- Google OAuth 2.0 with PKCE (S256), Desktop-app client type
- System browser for consent — **NOT YET BUILT**; the current implementation opens a
  `window.open` popup (`frontend/src/features/accounts/AccountsPage.tsx:22`)
- Scopes: `userinfo.email`, `gmail.readonly`. No send or modify scope. This is
  deliberate and enforced in `backend/app/mail/providers/gmail.py:20-23`
- Access + refresh tokens encrypted with Windows DPAPI
- Initial sync, incremental history sync, and progressive All Mail backfill
- Token refresh with re-encryption on every refresh
- Disconnect (`DELETE /api/accounts/{id}`) and account deletion

## 9. Local AI

- Ollama at a configurable `OLLAMA_BASE_URL`, default `http://127.0.0.1:11434`
- Default model `qwen3:4b`
- Structured JSON output via Pydantic schemas passed to Ollama's `format` parameter
- Content-fingerprint + model + schema-version cache key
- Prompt-injection defence in the analysis prompt (rule 9, `backend/app/ai/service.py:41`)
- HTML/quote/signature/base64 stripping before inference (`_prepare_body`)
- Runtime supervision with a bounded backoff schedule `(5, 10, 20, 30, 30)`
- One-time Ollama auto-start attempt when the binary is found
- Inference metrics recorded to SQLite (`inference_metrics` table)

## 10. Model management

**NOT YET BUILT.** Today the model name is a build-time constant. Required product
states: `MODEL_RUNTIME_MISSING`, `MODEL_RUNTIME_STARTING`, `MODEL_DOWNLOAD_REQUIRED`,
`MODEL_DOWNLOADING`, `MODEL_READY`, `MODEL_FAILED`, with real progress, size, disk
requirement, cancel, and resume. See `docs/Phases.md` Phase 2.

## 11. Privacy model

Stated precisely, because the product's credibility depends on it being exact.

| Data | Where it goes | Evidence |
| --- | --- | --- |
| Mail content | The local Ollama endpoint only | `backend/app/ai/ollama_client.py`; no cloud fallback exists in the code |
| OAuth tokens | Encrypted with Windows DPAPI, stored in local SQLite | `backend/app/db/secure_store.py` |
| Mail mirror | `%LOCALAPPDATA%\AlfredData\alfred.sqlite3` | `backend/app/config.py:23-34` |
| Analytics | None. Alfred contains no analytics code. | verified by search |
| Error logs | `%LOCALAPPDATA%\AlfredData\logs\`, rotating, 1 MB x 2 | `backend/sidecar.py:31-34` |

Known deviation from the intended model: if DPAPI is unavailable or fails, tokens fall
back to reversible base64 with no log line (`backend/app/db/secure_store.py:41-44`).
This is a defect, tracked in `docs/Memory.md`, not an accepted design.

## 12. Settings

Present: theme preference, account list, build identity. **NOT YET BUILT:** model
selection, sync scope, AI behaviour, data location, log access, backup/restore.

## 13. Public website

**NOT YET BUILT.** No website of any kind exists in the repository — verified by
searching for every common site framework config and site directory name; there are
zero matches. Required surface and content rules are in `docs/Phases.md` Phase 6 and
`docs/Rules.md` §UI.

Two constraints on the website plan, stated now so they are not discovered late:

1. **No page may be created to fill a route list.** The required page list in
   `docs/Phases.md` is a ceiling, not a quota.
2. **`/case-studies` cannot ship.** It requires real customers. Until real evidence
   exists, the honest options are to omit the route or to publish a page that explains
   Alfred is pre-release and has no case studies. A page of invented testimonials is
   forbidden by `docs/Rules.md` and by the product's own integrity.

## 14. Installer and distribution

Present: NSIS per-user installer, configured and built locally; `externalBin` sidecar;
release manifest with SHA-256 checksums; a read-only install verifier.

**NOT YET BUILT:** MSI, Authenticode signing, publisher metadata, any published
release, any update mechanism, CI that produces artifacts.

## 15. Non-goals

These are rejected deliberately. Adding them requires a new ADR.

1. Sending, replying to, deleting, or modifying mail.
2. Non-Gmail providers.
3. macOS or Linux desktop builds.
4. Cloud AI inference, or any AI fallback that leaves the machine.
5. Team, multi-user, or shared-mailbox support.
6. A mobile application.
7. Telemetry of any kind inside Alfred.
8. Alfred-as-a-service or any hosted component.
9. A calendar, contacts, or task-manager replacement. Alfred derives tasks *from mail*;
   it is not a task manager.

## 16. Acceptance criteria

The product is production-ready only when all of the following are evidenced. Each maps
to a gate in `docs/Phases.md`.

### Startup and process
- [ ] AC-1 A single launch produces exactly one visible Alfred window. **Currently
      fails** — `desktop/src-tauri/tauri.conf.json:20` sets `"visible": false` and the
      only `window.show()` (`desktop/src-tauri/src/main.rs:481`) is inside the
      single-instance callback, so the first launch shows nothing.
- [ ] AC-2 No console window appears in a release build.
      (`main.rs:1` sets `windows_subsystem = "windows"`; needs installer-level proof.)
- [ ] AC-3 Closing Alfred leaves no `alfred-backend.exe` process. **Currently
      unproven** — `main.rs:510` uses `try_lock()`, which silently skips shutdown when
      the supervisor mutex is contended.
- [ ] AC-4 A cold backend start that exceeds the timeout produces a named failure
      state with a diagnostic code, not a raw error string.
- [ ] AC-5 Backend stdout/stderr reach the log in a packaged build. **Currently
      fails** — `main.rs:105,108` call `log::debug!` and no logger is ever installed.

### Gmail
- [ ] AC-6 Consent opens in the system browser. **Currently fails** — popup is used.
- [ ] AC-7 A denied or cancelled consent shows a real message and leaves the app usable.
- [ ] AC-8 Expired authorization refreshes transparently; unrecoverable expiry prompts
      reconnect.
- [ ] AC-9 The connected account is visibly identified, with disconnect and reconnect.

### Local AI
- [ ] AC-10 A machine with no Ollama reaches a usable first-run state with clear
      instructions. **Currently fails** — no first-run model flow exists.
- [ ] AC-11 Model download shows real progress, real size, and supports cancel/retry.
      **NOT YET BUILT.**
- [ ] AC-12 Killing Ollama mid-session pauses AI work and the mailbox stays usable.
      (Believed to hold; needs a manual test.)

### Data and correctness
- [ ] AC-13 Schema migration is fail-closed and leaves a restorable backup.
      (Believed to hold — `MigrationSafetyError`, `database.py:503-505`.)
- [ ] AC-14 Search never returns a message the user cannot open.
- [ ] AC-15 Every AI-derived task and deadline is traceable to a source message.

### Interface
- [ ] AC-16 One primary H1 per page; the default Mail view currently has none.
- [ ] AC-17 Skip-to-content exists; currently absent.
- [ ] AC-18 Full keyboard operation, including the `radiogroup` in `ThemeToggle`, which
      currently has no arrow-key handling.
- [ ] AC-19 `prefers-reduced-motion` honoured. (Believed to hold; CSS-only.)
- [ ] AC-20 No unexpected console errors. **Currently fails** — a React
      setState-during-render warning is emitted by `MailWorkspace` in the test run.

### Build and distribution
- [ ] AC-21 No source maps in the production bundle. **Currently holds** — verified,
      0 `.map` files in `frontend/dist`.
- [ ] AC-22 Document title is `Alfred`, never Vite/React/localhost. **Currently holds.**
- [ ] AC-23 The installer is built from source in CI, not only on one machine.
- [ ] AC-24 Install, upgrade, and uninstall are verified on a clean machine.
- [ ] AC-25 Release artifacts carry checksums. (Manifest generator exists; no release
      is published.)

### Public website
- [ ] AC-26 Every page has unique title, description, and canonical URL.
- [ ] AC-27 `/robots.txt`, `/sitemap.xml`, `/llms.txt`, and `favicon.ico` resolve.
- [ ] AC-28 Structured data validates and contains no fabricated ratings, reviews,
      counts, or locations.
- [ ] AC-29 No fake testimonials, metrics, or customer photography anywhere.

### Security
- [ ] AC-30 The Google OAuth client secret is not extractable from the shipped binary.
      **Currently fails** — `backend/build_sidecar.py:33-38` embeds it in
      `production.env`, which PyInstaller extracts at runtime.
- [ ] AC-31 DPAPI failure is loud, not a silent downgrade to base64.
- [ ] AC-32 The runtime session token comes from a CSPRNG. **Currently fails** —
      `main.rs:224-240` derives it from `RandomState` hashing of clock and PID.
- [ ] AC-33 Token comparison is constant-time. **Currently fails** — `main.py:566`.
- [ ] AC-34 `postMessage` from the OAuth popup is origin-checked. **Currently fails** —
      `AccountsPage.tsx:41-45` does not check `event.origin`.
- [ ] AC-35 No Gmail content, token, or credential appears in any log.
- [ ] AC-36 The production CSP does not permit the Vite dev origin. **Currently fails**
      — `tauri.conf.json:25` allows `http://localhost:5173`.
