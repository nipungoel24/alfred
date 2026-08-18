---
type: journal
layer: meta
status: active
tags:
  - documentation
---

# Engineering Journal

Milestones as evidenced by git history and repository state. High-level; details live in the linked notes.

## 1. Pre-Alfred prototype

`src/` + `config/` + `run_app.py`: Streamlit UI, LangGraph agents, Groq/Llama cloud inference, CSV ingest, session-only state, eager drafts. Documented in `docs/architecture/current-system.md` as the system *pre-migration*. Retained in-tree as history, not runtime ([[Entry Points]]).

## 2. Gmail OAuth + real verification

PKCE popup flow, DPAPI token storage, callback hardening (`fix: harden Gmail OAuth callback…`). Verified against the real mailbox — no resets, incremental-only ([[Gmail E2E Testing]], [[Gmail OAuth Flow]]).

## 3. Performance hardening

SQLite optimization (WAL, indexes, FTS), persistent analysis jobs, SSE request-storm fix (debounced invalidation), priority queue. Baselines in `docs/engineering/performance-baseline.md` / `performance-final.md` ([[Performance Benchmarks]], [[ADR-007 - Background Analysis Queue]]).

## 4. Task derivation redesign

Action candidates separated from tasks; noise/ownership/confidence gates; fingerprints; versioned derivation with safe migration preserving user state ([[ADR-008 - Separate Action Candidates From Tasks]], [[ADR-009 - Versioned Task Derivation]]).

## 5. Mailbox model + eligibility

Gmail labels → mailbox state → categories → pipeline eligibility as one policy module; label history events recompute everything without body re-fetch; source rows never deleted to hide mail ([[ADR-014 - Mail Eligibility Policy]], [[Data Ownership]]).

## 6. All Mail + backend-owned backfill

Inbox/All Mail scopes, sent/archived semantics, progressive backfill moved from frontend polling to a durable backend job with typed state, bounded pages, backoff, and restart-resume ([[All Mail Backfill Flow]]).

## 7. Frontend redesigns

Mattered-style multi-pane workspace → premium ambient glass system → reader document surface + intelligence companion refinements ([[Design System]], [[Mail Workspace Screen]]).

## Related

- [[Project Status]]
- [[ADR Index]]
