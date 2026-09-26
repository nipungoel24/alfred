---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.dismiss_task
source: backend/app/db/repositories.py
line: 861
status: active
tags: [database, function]
---

# dismiss_task

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Durable user rejection ("Not a task").

## Location

`backend/app/db/repositories.py:861`

## Signature

```python
(self, task_id: str) -> bool
```

## Parameters

- `self`
- `task_id` (`str`)

## Returns

`bool`

## Writes

- [[table_tasks]]

## Side Effects

- SQLite
