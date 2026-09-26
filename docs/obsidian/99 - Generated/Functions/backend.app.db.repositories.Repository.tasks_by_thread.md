---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.tasks_by_thread
source: backend/app/db/repositories.py
line: 827
status: active
tags: [database, function]
---

# tasks_by_thread

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Get tasks linked to a specific thread, optionally account-scoped.

## Location

`backend/app/db/repositories.py:827`

## Signature

```python
(self, thread_id: str, account_id: str | None = None) -> list[Task]
```

## Parameters

- `self`
- `thread_id` (`str`)
- `account_id` (`str | None`)

## Returns

`list[Task]`

## Reads

- [[table_emails]]
- [[table_tasks]]

## Side Effects

- SQLite
