---
type: function
generated: true
language: python
layer: backend
module: backend.app.services.task_migration.TaskMigrationService
qualified_name: backend.app.services.task_migration.TaskMigrationService.run_migration
source: backend/app/services/task_migration.py
line: 15
status: active
tags: [backend, function]
---

# run_migration

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Run safe task migration over existing analyses.

## Location

`backend/app/services/task_migration.py:15`

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

- [[backend.app.services.task_derivation.derive_tasks|derive_tasks]] (calls)

## Writes

- [[table_tasks]]

## Side Effects

- SQLite
