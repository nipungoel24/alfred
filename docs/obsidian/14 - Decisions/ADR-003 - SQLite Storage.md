---
type: adr
layer: meta
status: active
tags:
  - architecture
  - database
---

# ADR-003 - SQLite Storage

## Status

Accepted

## Context

Alfred is single-user, local, and needs durability across restarts with zero operational overhead.

## Decision

One SQLite file (WAL, FTS5) in AppData, accessed via a single Repository class; no ORM.

## Alternatives Considered

- ORM (SQLAlchemy) — abstraction cost without multi-dialect need.
- Separate DB server — absurd for a desktop app.

## Why

SQLite gives transactions, FTS5 search, and a file the user can back up; raw SQL keeps migrations and the durable job queue explicit.

## Consequences

- Schema evolution is hand-written additive migrations ([[Migrations]]).
- Concurrency is single-process, two-worker — enforced by design, not by the engine ([[Database Architecture]]).

## Related Code

- [[backend.app.db.database]]
- [[backend.app.db.repositories.Repository|Repository]]

## Related Documentation

- [[Database Overview]]
