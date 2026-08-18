---
type: architecture
layer: ai
status: active
tags:
  - ai
---

# Task Intelligence

How Alfred decides something is *your* task, not just text — [[backend.app.services.task_derivation]].

## From candidates to tasks

The model emits **action candidates** ([[backend.app.schemas.ActionItem]]). Derivation applies four gates before a row reaches [[tasks]]:

1. **Length & noise** — ≥10 chars; a curated regex corpus kills phishing/CTA patterns ("click here", "verify credentials", payment updates…).
2. **Ownership** — owner must be the user (or blank); third-party owners are dropped unless a relay is explicit.
3. **Category economics** — newsletter/promotion/notification sources only produce tasks when priority is high/urgent *and* needs_reply; receipts never.
4. **Deduplication** — fingerprint `sha256(thread_id | normalized action)`; dedupes within an email, across emails, and across re-derivations.

## Confidence

`high` (needs_reply ± explicit deadline), `medium` (high-priority mail), `low` otherwise — displayed per task and stored in `tasks.confidence` ([[tasks]]).

## Separation of powers

Action candidates live in the analysis; tasks are the validated projection. Changing the derivation rules never re-runs the LLM — it rebuilds from cached analyses ([[ADR-008 - Separate Action Candidates From Tasks]], [[ADR-009 - Versioned Task Derivation]]).

## Related

- [[Task Derivation Flow]]
- [[Deadline Extraction Flow]]
- [[backend.app.services.task_migration.TaskMigrationService|TaskMigrationService]]
