---
type: adr
layer: meta
status: active
tags:
  - architecture
  - ai
  - critical-path
---

# ADR-009 - Versioned Task Derivation

## Status

Accepted

## Context

After the derivation redesign ([[ADR-008 - Separate Action Candidates From Tasks]]), old tasks derived by v1 rules were still in the database — some wrong, some duplicating user-edited tasks.

## Decision

- `derivation_version` stamps every task.
- Fingerprints (`sha256(thread|normalized action)`) make derivation idempotent across versions.
- Migrations **re-derive from cached analyses** (no LLM), reconcile by fingerprint, preserve user status/id/created_at, and only prune *pending* obsolete tasks ([[backend.app.services.task_migration.TaskMigrationService|TaskMigrationService]]).

## Why

Re-derivation is cheap (local), safe (user state wins), and repeatable (versioned) — the pattern for every future rule change.

## Consequences

- Source mail and cached analyses are never touched by migrations ([[Data Ownership]]).
- Rebuild runs at startup when the version changes ([[Application Startup Flow]]).

## Related Code

- [[backend.app.services.task_derivation.rebuild_tasks_from_analyses|rebuild_tasks_from_analyses]]
- [[backend.app.services.task_migration.TaskMigrationService|TaskMigrationService]]

## Related Documentation

- [[Task Derivation Flow]]
- [[Migration Testing]]
