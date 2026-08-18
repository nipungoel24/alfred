---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository._update_fts_one
source: backend/app/db/repositories.py
line: 354
status: active
tags: [database, function]
---

# _update_fts_one

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Keep the FTS5 index in sync for a single upsert.

## Location

`backend/app/db/repositories.py:354`

## Signature

```python
(self, email_id: str, email: Email)
```

## Parameters

- `self`
- `email_id` (`str`)
- `email` (`Email`)

## Writes

- [[table_emails]]
- [[table_emails_fts]]

## Side Effects

- SQLite
