---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.set_task_priority
source: backend/app/db/repositories.py
line: 873
status: active
tags: [database, function]
---

# set_task_priority

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Explicit user priority edit. Records priority_override so future

## Location

`backend/app/db/repositories.py:873`

## Signature

```python
(self, task_id: str, priority: str) -> bool
```

## Parameters

- `self`
- `task_id` (`str`)
- `priority` (`str`)

## Returns

`bool`

## Writes

- [[table_tasks]]

## Side Effects

- SQLite
