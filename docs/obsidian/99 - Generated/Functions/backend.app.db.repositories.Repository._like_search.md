---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository._like_search
source: backend/app/db/repositories.py
line: 395
status: active
tags: [database, function]
---

# _like_search

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Substring fallback used when FTS is unavailable or unusable.

## Location

`backend/app/db/repositories.py:395`

## Signature

```python
(self, query: str, limit: int) -> list[Email]
```

## Parameters

- `self`
- `query` (`str`)
- `limit` (`int`)

## Returns

`list[Email]`

## Calls

- `model_validate_json` (`backend.app.schemas.Email.model_validate_json`, calls-inferred)

## Reads

- [[table_emails]]

## Side Effects

- SQLite
