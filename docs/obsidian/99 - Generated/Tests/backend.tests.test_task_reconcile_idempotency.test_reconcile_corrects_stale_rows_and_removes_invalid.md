---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_task_reconcile_idempotency
qualified_name: backend.tests.test_task_reconcile_idempotency.test_reconcile_corrects_stale_rows_and_removes_invalid
source: backend/tests/test_task_reconcile_idempotency.py
line: 131
status: active
tags: [test, function, test]
---

# test_reconcile_corrects_stale_rows_and_removes_invalid

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_reconcile_corrects_stale_rows_and_removes_invalid` in `backend/tests/test_task_reconcile_idempotency.py`.

## Location

`backend/tests/test_task_reconcile_idempotency.py:131`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.tasks_all|tasks_all]] (calls)
- [[backend.app.services.task_derivation.reconcile_tasks_from_analyses|reconcile_tasks_from_analyses]] (calls)

## Reads

- [[table_tasks]]

## Side Effects

- SQLite
