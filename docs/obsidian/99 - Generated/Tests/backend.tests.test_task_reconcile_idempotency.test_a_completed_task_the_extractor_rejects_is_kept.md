---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_task_reconcile_idempotency
qualified_name: backend.tests.test_task_reconcile_idempotency.test_a_completed_task_the_extractor_rejects_is_kept
source: backend/tests/test_task_reconcile_idempotency.py
line: 247
status: active
tags: [test, function, test]
---

# test_a_completed_task_the_extractor_rejects_is_kept

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_a_completed_task_the_extractor_rejects_is_kept` in `backend/tests/test_task_reconcile_idempotency.py`.

## Location

`backend/tests/test_task_reconcile_idempotency.py:247`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- `commit` (`backend.app.db.repositories.Repository.con.commit`, calls-inferred)
- `execute` (`backend.app.db.repositories.Repository.con.execute`, calls-inferred)
- [[backend.app.schemas.ActionItem|ActionItem]] (calls)
- [[backend.app.services.task_derivation.reconcile_tasks_from_analyses|reconcile_tasks_from_analyses]] (calls)

## Reads

- [[table_tasks]]

## Writes

- [[table_tasks]]

## Side Effects

- SQLite
