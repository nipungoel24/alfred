---
type: architecture
layer: test
status: active
tags:
  - test
---

# Performance Benchmarks

Measured performance work, its tooling, and its limits.

## Harness

`backend/benchmarks/` — scripts that exercise the repository/AI paths and record timings; historical baselines in `docs/engineering/performance-baseline.md` and `performance-final.md`. Ongoing per-inference data accumulates in [[inference_metrics]].

## Historical focus (git history)

- SQLite optimization (WAL, indexes, batch upserts, FTS).
- Analysis queue priority ordering and persistence ([[ADR-007 - Background Analysis Queue]]).
- SSE request-storm fix (debounced invalidation, [[ADR-011 - SSE Progress]]).
- Category/scope queries verified via `EXPLAIN QUERY PLAN` ([[Indexes]]).

## Current posture

- Category switch is client-cached (React Query) — no reanalysis.
- Backfill is bounded and rate-limited ([[All Mail Backfill Flow]]).
- Virtualization keeps the DOM small regardless of mailbox size ([[ADR-012 - Inbox Virtualization]]).

## Related

- [[AI Performance]]
- [[Database Overview]]
