---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_task_reconcile_idempotency
qualified_name: backend.tests.test_task_reconcile_idempotency.test_migration_service_is_idempotent
source: backend/tests/test_task_reconcile_idempotency.py
line: 213
status: active
tags: [test, function, test]
---

# test_migration_service_is_idempotent

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_migration_service_is_idempotent` in `backend/tests/test_task_reconcile_idempotency.py`.

## Location

`backend/tests/test_task_reconcile_idempotency.py:213`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.tasks_all|tasks_all]] (calls)
- [[backend.app.services.task_migration.TaskMigrationService|TaskMigrationService]] (calls)

## Reads

- [[table_tasks]]

## Side Effects

- SQLite
