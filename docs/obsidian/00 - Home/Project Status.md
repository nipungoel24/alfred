---
type: architecture
layer: meta
status: active
tags:
  - system
---

# Project Status

Evidence-based status of the Alfred system. Classifications: **implemented** (code exists), **verified** (automated tests), **real-world verified** (exercised against the real Gmail mailbox), **native-tested** (inside the packaged desktop shell), **planned** (not built).

## Implemented + verified

- Gmail OAuth (PKCE, offline access) — [[Gmail OAuth Flow]]; mock-tested in [[backend.tests.test_gmail_mock]], real-world verified.
- Gmail sync (initial, incremental historyId, pagination) — [[Gmail Incremental Sync Flow]]; real-world verified (no mailbox reset).
- Mailbox model: labels → mailbox state → categories → pipeline eligibility — [[backend.app.mail.eligibility.MailEligibilityPolicy]]; corpus-tested in [[backend.tests.test_eligibility]].
- All Mail (inbox + archived + sent; spam/trash/draft excluded) with backend-owned progressive backfill — [[All Mail Backfill Flow]]; tested in [[backend.tests.test_allmail]] and [[backend.tests.test_backfill_jobs]]; real-world verified including restart-resume.
- Local analysis queue with durable jobs, priorities, retries — [[Background Analysis Job Flow]].
- Structured AI analysis (qwen3:4b via Ollama) — [[Email Analysis Flow]]; golden-corpus tested.
- Task derivation v2 with fingerprints + safe migration — [[Task Derivation Flow]], [[ADR-009 - Versioned Task Derivation]]; tested in [[backend.tests.test_task_derivation]] and [[backend.tests.test_task_migration]].
- Briefing + draft generation — [[Briefing Generation Flow]], [[Draft Generation Flow]].
- SSE progress + React Query frontend — [[SSE Progress Flow]], [[ADR-011 - SSE Progress]].
- Light/dark theme system, Mattered-style mail workspace, premium ambient UI — [[Design System]], [[Frontend Overview]]; tested in the Vitest suite.
- DPAPI token storage on Windows — [[DPAPI]], [[Token Storage]].

## Partially verified

- Desktop packaging: Tauri shell + sidecar spawn implemented in `desktop/src-tauri/src/main.rs`; the sidecar binary has been built (`alfred-backend-x86_64-pc-windows-msvc.spec`, `desktop/src-tauri/binaries/alfred-backend.exe`), but the packaged NSIS bundle has **not** been end-to-end verified in this repository's history — treat as unproven packaging.
- Full-mailbox backfill at scale: verified on the connected mailbox (~116 messages); enormous-mailbox behavior (thousands of messages) not exercised.
- 1920×1080 / 1280×720 visual QA of the latest visual pass: pending human review.

## Planned / out of scope (Round 1)

- Sending replies, draft editing, multiple providers (IMAP/Outlook), cloud AI, calendar — deliberately excluded; see [[Round 1 Scope]].
- Native Tauri QA pass — explicitly deferred; see [[Desktop Architecture]].

## Known constraints

- Ollama must be running locally for analysis/briefing; unavailability is degraded gracefully ([[AI Failure Handling]]).
- Legacy prototype code (`src/`, `config/`, `run_app.py` — Streamlit + Groq + LangGraph) remains in the tree but is not part of Alfred; see [[Engineering Journal]] (Engineering Journal).
