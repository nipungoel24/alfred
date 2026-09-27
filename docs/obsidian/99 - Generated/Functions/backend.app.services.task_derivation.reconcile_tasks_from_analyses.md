---
type: function
generated: true
language: python
layer: backend
module: backend.app.services.task_derivation
qualified_name: backend.app.services.task_derivation.reconcile_tasks_from_analyses
source: backend/app/services/task_derivation.py
line: 316
status: active
tags: [backend, function]
---

# reconcile_tasks_from_analyses

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Make the tasks table match the current derivation logic. The one path.

## Location

`backend/app/services/task_derivation.py:316`

## Signature

```python
(repo, model: str) -> ReconcileReport
```

## Parameters

- `repo`
- `model` (`str`)

## Returns

`ReconcileReport`

## Calls

- [[backend.app.db.repositories.Repository.all_analyses_with_emails|all_analyses_with_emails]] (calls)
- [[backend.app.db.repositories.Repository.tasks_all|tasks_all]] (calls)
- `now` (`datetime.datetime.now`, calls-inferred)

## Called By

- [[backend.app.services.task_migration.TaskMigrationService.run_migration|run_migration]]
- [[backend.tests.test_task_reconcile_idempotency.test_a_completed_task_the_extractor_rejects_is_kept|test_a_completed_task_the_extractor_rejects_is_kept]]
- [[backend.tests.test_task_reconcile_idempotency.test_duplicate_stored_rows_collapse_to_one|test_duplicate_stored_rows_collapse_to_one]]
- [[backend.tests.test_task_reconcile_idempotency.test_pending_rejected_task_is_removed|test_pending_rejected_task_is_removed]]
- [[backend.tests.test_task_reconcile_idempotency.test_reconcile_corrects_stale_rows_and_removes_invalid|test_reconcile_corrects_stale_rows_and_removes_invalid]]
- [[backend.tests.test_task_reconcile_idempotency.test_reconcile_normalizes_an_existing_stale_row_in_place|test_reconcile_normalizes_an_existing_stale_row_in_place]]
- [[backend.tests.test_task_reconcile_idempotency.test_reconcile_on_a_copy_of_the_live_database_is_idempotent|test_reconcile_on_a_copy_of_the_live_database_is_idempotent]]
- [[backend.tests.test_task_reconcile_idempotency.test_running_the_migration_twice_changes_nothing_the_second_time|test_running_the_migration_twice_changes_nothing_the_second_time]]
- [[backend.tests.test_task_reconcile_idempotency.test_source_linkage_survives|test_source_linkage_survives]]
- [[backend.tests.test_task_reconcile_idempotency.test_two_messages_with_the_same_action_do_not_collapse|test_two_messages_with_the_same_action_do_not_collapse]]
- [[backend.tests.test_task_reconcile_idempotency.test_user_state_is_preserved_across_a_reconcile|test_user_state_is_preserved_across_a_reconcile]]

## Reads

- [[table_email_analysis]]
- [[table_emails]]
- [[table_tasks]]

## Writes

- [[table_tasks]]

## Side Effects

- SQLite
