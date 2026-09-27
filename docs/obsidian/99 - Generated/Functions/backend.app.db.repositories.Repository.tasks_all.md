---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.tasks_all
source: backend/app/db/repositories.py
line: 793
status: active
tags: [database, function]
---

# tasks_all

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Every persisted task row in every state, including dismissed.

## Location

`backend/app/db/repositories.py:793`

## Signature

```python
(self) -> list[Task]
```

## Parameters

- `self`

## Returns

`list[Task]`

## Called By

- [[backend.app.services.task_derivation.reconcile_tasks_from_analyses|reconcile_tasks_from_analyses]]
- [[backend.tests.test_task_reconcile_idempotency.test_duplicate_stored_rows_collapse_to_one|test_duplicate_stored_rows_collapse_to_one]]
- [[backend.tests.test_task_reconcile_idempotency.test_migration_service_is_idempotent|test_migration_service_is_idempotent]]
- [[backend.tests.test_task_reconcile_idempotency.test_pending_rejected_task_is_removed|test_pending_rejected_task_is_removed]]
- [[backend.tests.test_task_reconcile_idempotency.test_reconcile_corrects_stale_rows_and_removes_invalid|test_reconcile_corrects_stale_rows_and_removes_invalid]]
- [[backend.tests.test_task_reconcile_idempotency.test_reconcile_normalizes_an_existing_stale_row_in_place|test_reconcile_normalizes_an_existing_stale_row_in_place]]
- [[backend.tests.test_task_reconcile_idempotency.test_running_the_migration_twice_changes_nothing_the_second_time|test_running_the_migration_twice_changes_nothing_the_second_time]]
- [[backend.tests.test_task_reconcile_idempotency.test_running_the_rebuild_twice_is_stable|test_running_the_rebuild_twice_is_stable]]
- [[backend.tests.test_task_reconcile_idempotency.test_source_linkage_survives|test_source_linkage_survives]]
- [[backend.tests.test_task_reconcile_idempotency.test_two_messages_with_the_same_action_do_not_collapse|test_two_messages_with_the_same_action_do_not_collapse]]
- [[backend.tests.test_task_reconcile_idempotency.test_user_state_is_preserved_across_a_reconcile|test_user_state_is_preserved_across_a_reconcile]]

## Reads

- [[table_tasks]]

## Side Effects

- SQLite
