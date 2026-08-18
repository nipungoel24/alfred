---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.delete_email
source: backend/app/db/repositories.py
line: 308
status: active
tags: [database, function]
---

# delete_email

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `delete_email` in `backend/app/db/repositories.py`.

## Location

`backend/app/db/repositories.py:308`

## Signature

```python
(self, email_id: str)
```

## Parameters

- `self`
- `email_id` (`str`)

## Writes

- [[table_emails]]
- [[table_emails_fts]]
- [[table_tasks]]

## Side Effects

- SQLite
