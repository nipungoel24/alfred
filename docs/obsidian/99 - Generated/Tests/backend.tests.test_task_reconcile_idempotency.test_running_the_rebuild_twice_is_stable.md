---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_task_reconcile_idempotency
qualified_name: backend.tests.test_task_reconcile_idempotency.test_running_the_rebuild_twice_is_stable
source: backend/tests/test_task_reconcile_idempotency.py
line: 203
status: active
tags: [test, function, test]
---

# test_running_the_rebuild_twice_is_stable

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_running_the_rebuild_twice_is_stable` in `backend/tests/test_task_reconcile_idempotency.py`.

## Location

`backend/tests/test_task_reconcile_idempotency.py:203`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.tasks_all|tasks_all]] (calls)
- [[backend.app.services.task_derivation.rebuild_tasks_from_analyses|rebuild_tasks_from_analyses]] (calls)

## Reads

- [[table_tasks]]

## Side Effects

- SQLite
