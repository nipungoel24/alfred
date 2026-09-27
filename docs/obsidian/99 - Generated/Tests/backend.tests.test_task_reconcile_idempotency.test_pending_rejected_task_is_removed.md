---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_task_reconcile_idempotency
qualified_name: backend.tests.test_task_reconcile_idempotency.test_pending_rejected_task_is_removed
source: backend/tests/test_task_reconcile_idempotency.py
line: 280
status: active
tags: [test, function, test]
---

# test_pending_rejected_task_is_removed

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_pending_rejected_task_is_removed` in `backend/tests/test_task_reconcile_idempotency.py`.

## Location

`backend/tests/test_task_reconcile_idempotency.py:280`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- `commit` (`backend.app.db.repositories.Repository.con.commit`, calls-inferred)
- `execute` (`backend.app.db.repositories.Repository.con.execute`, calls-inferred)
- [[backend.app.db.repositories.Repository.tasks_all|tasks_all]] (calls)
- [[backend.app.services.task_derivation.reconcile_tasks_from_analyses|reconcile_tasks_from_analyses]] (calls)

## Reads

- [[table_tasks]]

## Writes

- [[table_tasks]]

## Side Effects

- SQLite
