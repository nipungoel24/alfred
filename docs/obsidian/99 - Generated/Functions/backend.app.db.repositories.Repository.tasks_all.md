---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.tasks_all
source: backend/app/db/repositories.py
line: 793
status: active
tags: [database, function]
---

# tasks_all

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Every persisted task row in every state, including dismissed.

## Location

`backend/app/db/repositories.py:793`

## Signature

```python
(self) -> list[Task]
```

## Parameters

- `self`

## Returns

`list[Task]`

## Reads

- [[table_tasks]]

## Side Effects

- SQLite
