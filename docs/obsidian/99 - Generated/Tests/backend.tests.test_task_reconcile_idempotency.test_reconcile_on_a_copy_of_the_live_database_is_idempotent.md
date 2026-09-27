---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_task_reconcile_idempotency
qualified_name: backend.tests.test_task_reconcile_idempotency.test_reconcile_on_a_copy_of_the_live_database_is_idempotent
source: backend/tests/test_task_reconcile_idempotency.py
line: 361
status: active
tags: [test, function, test]
---

# test_reconcile_on_a_copy_of_the_live_database_is_idempotent

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

The real 291-row backlog, on a copy. The live file is never opened.

## Location

`backend/tests/test_task_reconcile_idempotency.py:361`

## Signature

```python
(tmp_path)
```

## Parameters

- `tmp_path`

## Calls

- [[backend.app.db.repositories.Repository|Repository]] (calls)
- [[backend.app.services.task_derivation.reconcile_tasks_from_analyses|reconcile_tasks_from_analyses]] (calls)
- `copy2` (`shutil.copy2`, calls-inferred)
- `connect` (`sqlite3.connect`, calls-inferred)

## Reads

- [[table_tasks]]

## Side Effects

- SQLite
