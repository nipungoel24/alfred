---
type: adr
layer: meta
status: active
tags:
  - architecture
  - ai
  - critical-path
---

# ADR-007 - Background Analysis Queue

## Status

Accepted

## Context

Analyzing mail is slow (seconds per email on local hardware) and must not block sync, the UI, or restarts.

## Decision

Analysis runs through a **durable SQLite job queue** ([[jobs]]) processed by a single in-process worker: idempotent deterministic ids, integer priorities, attempts/max_attempts, `not_before` scheduling, retryable vs terminal failures.

## Alternatives Considered

- On-demand only (analyze when opened) — first-use latency everywhere; the briefing needs a warm cache.
- Celery/Redis — external infrastructure for a desktop app; rejected.

## Why

A table-backed queue makes every background loop restart-proof and introspectable; priorities encode policy ([[backend.app.mail.eligibility.MailEligibilityPolicy.analysis_queue_priority|analysis_queue_priority]]) so Promotions/Social are lazily analyzed.

## Consequences

- Two workers (analysis + backfill) share the queue discipline ([[All Mail Backfill Flow]]).
- Eligibility is re-checked at pickup — mid-queue spam moves cancel jobs.

## Related Code

- [[backend.app.main._analysis_worker]]
- [[backend.app.db.repositories.Repository.next_job|next_job]]

## Related Documentation

- [[Background Analysis Job Flow]]
- [[AI Failure Handling]]
