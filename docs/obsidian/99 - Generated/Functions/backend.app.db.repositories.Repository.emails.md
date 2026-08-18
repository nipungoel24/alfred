---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.emails
source: backend/app/db/repositories.py
line: 73
status: active
tags: [database, function]
---

# emails

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Fetch emails ordered by received_at descending.

## Location

`backend/app/db/repositories.py:73`

## Signature

```python
(self, account_id = None, limit = 500, offset = 0)
```

## Parameters

- `self`
- `account_id`
- `limit`
- `offset`

## Calls

- `model_validate_json` (`backend.app.schemas.Email.model_validate_json`, calls-inferred)

## Reads

- [[table_emails]]

## Side Effects

- SQLite
