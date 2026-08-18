---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.emails_missing_labels
source: backend/app/db/repositories.py
line: 174
status: active
tags: [database, function]
---

# emails_missing_labels

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

IDs of cached Gmail messages whose label set is unknown.

## Location

`backend/app/db/repositories.py:174`

## Signature

```python
(self, account_id: str | None = None, limit: int = 200) -> list[str]
```

## Parameters

- `self`
- `account_id` (`str | None`)
- `limit` (`int`)

## Returns

`list[str]`

## Reads

- [[table_emails]]

## Side Effects

- SQLite
