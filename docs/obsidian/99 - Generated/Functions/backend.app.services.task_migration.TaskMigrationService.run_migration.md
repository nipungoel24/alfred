---
type: function
generated: true
language: python
layer: backend
module: backend.app.services.task_migration.TaskMigrationService
qualified_name: backend.app.services.task_migration.TaskMigrationService.run_migration
source: backend/app/services/task_migration.py
line: 23
status: active
tags: [backend, function]
---

# run_migration

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Reconcile every task against the current derivation logic.

## Location

`backend/app/services/task_migration.py:23`

## Signature

```python
(self, model: str) -> Tuple[int, int]
```

## Parameters

- `self`
- `model` (`str`)

## Returns

`Tuple[int, int]`

## Calls

- [[backend.app.services.task_derivation.reconcile_tasks_from_analyses|reconcile_tasks_from_analyses]] (calls)

## Side Effects

- none statically observed
