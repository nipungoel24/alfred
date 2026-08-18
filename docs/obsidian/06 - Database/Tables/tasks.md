---
type: database-table
layer: database
status: active
source: backend/app/db/database.py
tags:
  - database
---

# tasks

The derived, user-actionable projection of mail — reconciled with user state, never sacred.

## Data classification

**Derived + user state.** Rows are machine-derived, but `status` (`pending`/`completed`) and deletions are user decisions. Re-derivation preserves them ([[backend.app.services.task_migration.TaskMigrationService|TaskMigrationService]]).

## Key columns

- `source_email_id` → [[emails]] (SET NULL on email delete), `source_thread_id` for thread-level dedupe.
- `fingerprint` — `sha256(thread|normalized action)`; the reconciliation key ([[backend.app.services.task_derivation.task_fingerprint]]).
- `derivation_version`, `confidence`, `due_at`, `priority` — derivation metadata.

Schema detail: [[table_tasks]].

## Written By

- [[backend.app.services.task_derivation.derive_tasks]] (via worker's `_derive_and_save_tasks`)
- [[backend.app.services.task_migration.TaskMigrationService.run_migration]]
- User mutations: [[POST --api-tasks-{task_id}-toggle]], [[DELETE --api-tasks-{task_id}]]

## Read By

- [[GET --api-tasks]] → active projection via [[backend.app.db.repositories.Repository.active_tasks]] (excludes tasks whose source email left the active inbox)
- [[frontend.src.features.tasks.TasksPage.TasksPage|TasksPage]]

## Migration rules

Source emails stay untouched when the task projection changes; completed/dismissed tasks survive re-derivation; obsolete *pending* tasks are removed ([[ADR-009 - Versioned Task Derivation]]).

## Related

- [[email_analysis]]
- [[Task Derivation Flow]]
- [[emails]]
