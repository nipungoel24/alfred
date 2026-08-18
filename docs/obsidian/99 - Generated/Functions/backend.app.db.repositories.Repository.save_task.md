---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.save_task
source: backend/app/db/repositories.py
line: 499
status: active
tags: [database, function]
---

# save_task

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `save_task` in `backend/app/db/repositories.py`.

## Location

`backend/app/db/repositories.py:499`

## Signature

```python
(self, task: Task)
```

## Parameters

- `self`
- `task` (`Task`)

## Calls

- `now` (`datetime.datetime.now`, calls-inferred)

## Writes

- [[table_tasks]]

## Side Effects

- SQLite
