---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository._update_fts_one
source: backend/app/db/repositories.py
line: 528
status: active
tags: [database, function]
---

# _update_fts_one

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Keep the FTS5 index in sync for a single upsert.

## Location

`backend/app/db/repositories.py:528`

## Signature

```python
(self, email_id: str, email: Email)
```

## Parameters

- `self`
- `email_id` (`str`)
- `email` (`Email`)

## Calls

- [[backend.app.db.database.fts_delete_supported|fts_delete_supported]] (calls)
- `getLogger` (`logging.getLogger`, calls-inferred)

## Reads

- [[table_emails]]
- [[table_emails_fts]]

## Writes

- [[table_emails_fts]]

## Side Effects

- SQLite
