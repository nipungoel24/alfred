---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_task_reconcile_idempotency
qualified_name: backend.tests.test_task_reconcile_idempotency.test_reconcile_normalizes_an_existing_stale_row_in_place
source: backend/tests/test_task_reconcile_idempotency.py
line: 149
status: active
tags: [test, function, test]
---

# test_reconcile_normalizes_an_existing_stale_row_in_place

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_reconcile_normalizes_an_existing_stale_row_in_place` in `backend/tests/test_task_reconcile_idempotency.py`.

## Location

`backend/tests/test_task_reconcile_idempotency.py:149`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- `execute` (`backend.app.db.repositories.Repository.con.execute`, calls-inferred)
- [[backend.app.db.repositories.Repository.tasks_all|tasks_all]] (calls)
- [[backend.app.services.task_derivation.reconcile_tasks_from_analyses|reconcile_tasks_from_analyses]] (calls)

## Reads

- [[table_tasks]]

## Writes

- [[table_tasks]]

## Side Effects

- SQLite
