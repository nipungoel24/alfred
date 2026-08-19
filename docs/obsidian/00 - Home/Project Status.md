---
type: architecture
layer: meta
status: active
tags:
  - system
---

# Project Status

Evidence-based status of the Alfred system. Classifications: **implemented** (code exists), **verified** (automated tests), **real-world verified** (exercised against the real Gmail mailbox), **native-tested** (inside the real Tauri window/sidecar), **installed-app tested** (from the NSIS-installed app), **packaged** (installer artifact exists).

## Implemented + verified + real-world verified

- Gmail OAuth (PKCE, offline) — [[Gmail OAuth Flow]]; mock-tested, real-world verified.
- Gmail sync (initial, incremental historyId, pagination) — [[Gmail Incremental Sync Flow]]; real-world verified, duplicates=0 through the packaged sidecar.
- Mailbox model + eligibility policy — corpus-tested ([[backend.tests.test_eligibility]]).
- All Mail + backend-owned backfill — tested + real-world restart-resume verified ([[All Mail Backfill Flow]]).
- Analysis queue, structured AI (qwen3:4b), task derivation v2, briefing/drafts — tested; golden corpus; real Ollama runs (including through the packaged sidecar).
- SSE progress — repaired in this pass (status endpoints previously referenced a removed queue object) and covered by tests.
- Light/dark premium UI — Vitest suite.
- Desktop session auth + dynamic port + graceful shutdown + single instance — [[ADR-015 - Desktop Session Authentication]], [[ADR-016 - Tauri-Owned Sidecar Lifecycle]]; backend-tested + live-verified.

## Native-tested + installed-app tested (this pass)

- Toolchain: rustc 1.90 / MSVC 14.44 / WebView2 151.
- `cargo fmt --check` / `cargo check` / `cargo clippy`: clean.
- Native window: opens, sidecar auto-starts on a dynamic port, health gate reveals the UI, close → 0 orphan processes, port released.
- Single instance: second launch focuses the first window; no second sidecar/DB writer.
- Force-kill recovery: app survives backend death; relaunch restores everything (149 emails / 87 analyses / 21 tasks / 88 succeeded jobs intact, no duplicates).
- Installed app: launched from Start Menu install (`%LOCALAPPDATA%\Alfred`), real AppData loaded, real Gmail incremental sync (28 messages, 0 duplicates), Ollama analysis + briefing 200 through the installed binary.
- Installer: NSIS `Alfred_0.1.0_x64-setup.exe` (41.7 MB), silent install verified, uninstall registration + Start Menu verified, uninstall preserves the SQLite database.

## Packaged but unsigned

- **Signing: UNSIGNED DEVELOPMENT RELEASE** — no Authenticode certificate; SmartScreen will warn. Blocking item for public distribution.
- Brand icon is a generated placeholder (`tools/generate_icons.py`) pending the approved Alfred mark.

## Partially verified / outstanding

- Fresh Google OAuth from the installed app: the existing account works (DPAPI decrypt + refresh + sync verified); a brand-new authorization flow has NOT been re-exercised end-to-end from the native window in this pass — do not claim it fixed until a fresh flow completes ([[Gmail OAuth Flow]]).
- Ollama outage UX inside the native window: implemented (StartupGate/offline states) and covered by frontend tests; not manually re-observed in the native webview.
- 1920×1080 / 1280×720 visual QA of the latest visual pass: pending human review.

## Known constraints

- Ollama remains a required external prerequisite ([[Round 1 Scope]]).
- Legacy prototype code (`src/`, `config/`, `run_app.py`) remains in-tree as history, not runtime.
