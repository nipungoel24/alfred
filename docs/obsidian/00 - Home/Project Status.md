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
- Analysis queue, structured AI (qwen3:4b), task derivation v2, briefing/drafts — tested; golden corpus; real Ollama runs through the packaged sidecar.
- SSE progress, light/dark premium UI — Vitest suite.
- Desktop session auth + dynamic port + graceful shutdown + single instance — backend-tested + live-verified ([[ADR-015 - Desktop Session Authentication]], [[ADR-016 - Tauri-Owned Sidecar Lifecycle]]).

## Native-tested + installed-app tested

- Toolchain: rustc 1.90 / MSVC 14.44 / WebView2 151; `cargo fmt/check/clippy` clean.
- Native window, sidecar auto-start on dynamic port, readiness gate, close → 0 orphans, single instance, force-kill recovery.
- **FRESH INSTALLED-APP OAUTH VERIFIED** (real Google consent, fresh isolated profile, first sync 50/0 duplicates, first-run AI 44 analyses + 9 tasks + briefing).
- Ollama outage/recovery verified with normal data (cached UI served, scoped 503, auto-recovery).
- Installer installed/uninstalled repeatedly; uninstall preserves the SQLite DB.

## Startup incident (fixed build ready for human confirmation)

A release-candidate field failure ("couldn't start its local service") was root-caused to backend readiness being coupled to Ollama startup, plus stale production bootstrap and retry behavior. The fix decouples `/health` from local AI preload and prevents packaged frontend fallback to dev defaults.

Follow-up installed-state testing also found a stale Start Menu/Desktop shortcut target pointing at another Windows profile. The hook-based repair attempt was removed because it read installer-process environment paths and could leak an agent/sandbox profile into shortcuts. Alfred now relies on standard Tauri NSIS `$INSTDIR` shortcut creation and a human-run read-only verifier.

Current automated evidence is limited to build/source/artifact validation. Final installed-app status requires the human to install the immutable NSIS artifact manually, run the read-only verifier, launch Alfred from Start Menu, and confirm the Inbox loads. See [[ADR-018 - Health-Before-Heavy-Startup]], [[Windows Packaging]], [[Windows Deployment Standard]], and [[Debugging]].

## Packaged but unsigned

- **Signing: UNSIGNED DEVELOPMENT RELEASE** — no Authenticode certificate; SmartScreen will warn.
- Brand icon is a generated placeholder (`tools/generate_icons.py`) pending the approved Alfred mark.

## Outstanding (human steps)

- Final visual QA at 1280×720 / 1366×768 / 1440×900 / 1920×1080 — no release-blocking defect known.
- Manual webview observation of offline UI states (verified via API surface + tests).

## Known constraints

- Ollama remains a required external prerequisite ([[Round 1 Scope]]).
- Legacy prototype code (`src/`, `config/`, `run_app.py`) remains in-tree as history, not runtime.
