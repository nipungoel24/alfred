---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_task_user_corrections
qualified_name: backend.tests.test_task_user_corrections.test_dismiss_hides_and_suppresses_rederivation
source: backend/tests/test_task_user_corrections.py
line: 54
status: active
tags: [test, function, test]
---

# test_dismiss_hides_and_suppresses_rederivation

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_dismiss_hides_and_suppresses_rederivation` in `backend/tests/test_task_user_corrections.py`.

## Location

`backend/tests/test_task_user_corrections.py:54`

## Signature

```python
(isolated_app)
```

## Parameters

- `isolated_app`

## Calls

- [[backend.app.services.task_derivation.rebuild_tasks_from_analyses|rebuild_tasks_from_analyses]] (calls)
- `TestClient` (`fastapi.testclient.TestClient`, calls-inferred)

## Side Effects

- network (HTTP)
