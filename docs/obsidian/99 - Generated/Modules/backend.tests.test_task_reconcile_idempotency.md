---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_task_reconcile_idempotency
source: backend/tests/test_task_reconcile_idempotency.py
status: active
tags: [module, backend]
---

# backend.tests.test_task_reconcile_idempotency

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_task_reconcile_idempotency.py`

## Imports

- `ActionItem` ← `backend.app.schemas.ActionItem`
- `Category` ← `backend.app.schemas.Category`
- `DERIVATION_VERSION` ← `backend.app.services.task_derivation.DERIVATION_VERSION`
- `Deadline` ← `backend.app.schemas.Deadline`
- `Email` ← `backend.app.schemas.Email`
- `EmailAnalysis` ← `backend.app.schemas.EmailAnalysis`
- `Path` ← `pathlib.Path`
- `Priority` ← `backend.app.schemas.Priority`
- `Repository` ← `backend.app.db.repositories.Repository`
- `Task` ← `backend.app.schemas.Task`
- `TaskMigrationService` ← `backend.app.services.task_migration.TaskMigrationService`
- `os` ← `os`
- `pytest` ← `pytest`
- `rebuild_tasks_from_analyses` ← `backend.app.services.task_derivation.rebuild_tasks_from_analyses`
- `reconcile_tasks_from_analyses` ← `backend.app.services.task_derivation.reconcile_tasks_from_analyses`
- `shutil` ← `shutil`
- `sqlite3` ← `sqlite3`
- `tempfile` ← `tempfile`

## Functions

- [[backend.tests.test_task_reconcile_idempotency._live_db|_live_db]]
- [[backend.tests.test_task_reconcile_idempotency.make_analysis|make_analysis]]
- [[backend.tests.test_task_reconcile_idempotency.make_email|make_email]]
- [[backend.tests.test_task_reconcile_idempotency.repo|repo]]
- [[backend.tests.test_task_reconcile_idempotency.seed_realistic_backlog|seed_realistic_backlog]]
- [[backend.tests.test_task_reconcile_idempotency.store|store]]
- [[backend.tests.test_task_reconcile_idempotency.temp_db|temp_db]]

## Tests

- [[backend.tests.test_task_reconcile_idempotency.test_a_completed_task_the_extractor_rejects_is_kept|test_a_completed_task_the_extractor_rejects_is_kept]]
- [[backend.tests.test_task_reconcile_idempotency.test_duplicate_stored_rows_collapse_to_one|test_duplicate_stored_rows_collapse_to_one]]
- [[backend.tests.test_task_reconcile_idempotency.test_migration_service_is_idempotent|test_migration_service_is_idempotent]]
- [[backend.tests.test_task_reconcile_idempotency.test_pending_rejected_task_is_removed|test_pending_rejected_task_is_removed]]
- [[backend.tests.test_task_reconcile_idempotency.test_reconcile_corrects_stale_rows_and_removes_invalid|test_reconcile_corrects_stale_rows_and_removes_invalid]]
- [[backend.tests.test_task_reconcile_idempotency.test_reconcile_normalizes_an_existing_stale_row_in_place|test_reconcile_normalizes_an_existing_stale_row_in_place]]
- [[backend.tests.test_task_reconcile_idempotency.test_reconcile_on_a_copy_of_the_live_database_is_idempotent|test_reconcile_on_a_copy_of_the_live_database_is_idempotent]]
- [[backend.tests.test_task_reconcile_idempotency.test_running_the_migration_twice_changes_nothing_the_second_time|test_running_the_migration_twice_changes_nothing_the_second_time]]
- [[backend.tests.test_task_reconcile_idempotency.test_running_the_rebuild_twice_is_stable|test_running_the_rebuild_twice_is_stable]]
- [[backend.tests.test_task_reconcile_idempotency.test_source_linkage_survives|test_source_linkage_survives]]
- [[backend.tests.test_task_reconcile_idempotency.test_two_messages_with_the_same_action_do_not_collapse|test_two_messages_with_the_same_action_do_not_collapse]]
- [[backend.tests.test_task_reconcile_idempotency.test_user_state_is_preserved_across_a_reconcile|test_user_state_is_preserved_across_a_reconcile]]

## Constants

- `MODEL`
