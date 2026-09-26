---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.delete_email
source: backend/app/db/repositories.py
line: 346
status: active
tags: [database, function]
---

# delete_email

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Delete an email and its FTS entry.

## Location

`backend/app/db/repositories.py:346`

## Signature

```python
(self, email_id: str)
```

## Parameters

- `self`
- `email_id` (`str`)

## Calls

- [[backend.app.db.database.fts_delete_supported|fts_delete_supported]] (calls)
- `getLogger` (`logging.getLogger`, calls-inferred)

## Reads

- [[table_emails]]

## Writes

- [[table_emails]]
- [[table_emails_fts]]
- [[table_tasks]]

## Side Effects

- SQLite
