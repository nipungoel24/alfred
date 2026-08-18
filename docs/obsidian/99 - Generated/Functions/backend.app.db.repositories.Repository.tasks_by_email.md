---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.tasks_by_email
source: backend/app/db/repositories.py
line: 575
status: active
tags: [database, function]
---

# tasks_by_email

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Get tasks linked to a specific email.

## Location

`backend/app/db/repositories.py:575`

## Signature

```python
(self, email_id: str) -> list[Task]
```

## Parameters

- `self`
- `email_id` (`str`)

## Returns

`list[Task]`

## Reads

- [[table_tasks]]

## Side Effects

- SQLite
