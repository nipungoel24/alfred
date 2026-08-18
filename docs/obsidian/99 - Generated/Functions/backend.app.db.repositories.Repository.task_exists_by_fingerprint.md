---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.task_exists_by_fingerprint
source: backend/app/db/repositories.py
line: 586
status: active
tags: [database, function]
---

# task_exists_by_fingerprint

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Check if a task with this fingerprint already exists.

## Location

`backend/app/db/repositories.py:586`

## Signature

```python
(self, fingerprint: str) -> bool
```

## Parameters

- `self`
- `fingerprint` (`str`)

## Returns

`bool`

## Called By

- [[backend.app.services.task_derivation.rebuild_tasks_from_analyses|rebuild_tasks_from_analyses]]

## Reads

- [[table_tasks]]

## Side Effects

- SQLite
