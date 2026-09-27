---
type: function
generated: true
language: python
layer: backend
module: backend.app.services.task_derivation
qualified_name: backend.app.services.task_derivation.rebuild_tasks_from_analyses
source: backend/app/services/task_derivation.py
line: 482
status: active
tags: [backend, function]
---

# rebuild_tasks_from_analyses

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Back-compatible wrapper. Prefer :func:`reconcile_tasks_from_analyses`.

## Location

`backend/app/services/task_derivation.py:482`

## Signature

```python
(repo, model: str) -> int
```

## Parameters

- `repo`
- `model` (`str`)

## Returns

`int`

## Called By

- [[backend.app.main._startup_background|_startup_background]]
- [[backend.tests.test_task_reconcile_idempotency.test_running_the_rebuild_twice_is_stable|test_running_the_rebuild_twice_is_stable]]
- [[backend.tests.test_task_user_corrections.test_derivation_never_overwrites_user_priority|test_derivation_never_overwrites_user_priority]]
- [[backend.tests.test_task_user_corrections.test_dismiss_hides_and_suppresses_rederivation|test_dismiss_hides_and_suppresses_rederivation]]

## Side Effects

- none statically observed
