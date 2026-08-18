---
type: architecture
layer: meta
status: active
tags:
  - architecture
  - critical-path
---

# Critical Execution Paths

The paths that must never break, in order of blast radius.

## 1. Database bootstrap ([[backend.app.db.database.connect]])

Every process start. Additive migrations + backfills + indexes must be idempotent — anything else bricks the app.

## 2. OAuth connect ([[Gmail OAuth Flow]])

PKCE + state + token exchange + DPAPI persist. Failure modes must fail closed (no partial accounts).

## 3. Incremental sync ([[Gmail Incremental Sync Flow]])

The freshness spine. Cursor commits after page completion; deletions are non-destructive; label history recomputes eligibility.

## 4. Analysis worker ([[backend.app.main._analysis_worker]])

Eligibility guard at pickup → fingerprint cache → [[backend.app.ai.service.AIService.analyze_email|analyze_email]] → save + metrics → task derivation. Retry/backoff discipline keeps Ollama outages survivable.

## 5. Task derivation ([[backend.app.services.task_derivation.derive_tasks]])

Deterministic gates + fingerprints; the only writer of machine tasks besides migration.

## 6. Backfill worker ([[backend.app.main._backfill_worker]])

Bounded pages, typed state, `not_before` scheduling — the mailbox-completeness spine.

## 7. Frontend data spine

React Query keys → typed API client → FastAPI → SQL. SSE is a hint, never the source of truth ([[ADR-011 - SSE Progress]]).

## Related

- [[Test Coverage Map]]
- [[Runtime Lifecycle]]
- [[Dependency Map]]
