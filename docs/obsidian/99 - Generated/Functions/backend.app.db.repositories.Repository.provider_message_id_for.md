---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.provider_message_id_for
source: backend/app/db/repositories.py
line: 115
status: active
tags: [database, function]
---

# provider_message_id_for

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Persisted provider message id for a local id (None when unknown).

## Location

`backend/app/db/repositories.py:115`

## Signature

```python
(self, email_id: str) -> str | None
```

## Parameters

- `self`
- `email_id` (`str`)

## Returns

`str | None`

## Reads

- [[table_emails]]

## Side Effects

- SQLite
