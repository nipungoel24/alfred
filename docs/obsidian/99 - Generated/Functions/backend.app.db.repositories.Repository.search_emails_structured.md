---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.search_emails_structured
source: backend/app/db/repositories.py
line: 406
status: active
tags: [database, function]
---

# search_emails_structured

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Structured search with filters applied at the database level.

## Location

`backend/app/db/repositories.py:406`

## Signature

```python
(self, filters: SearchFilters, account_id: str | None = None, limit = 100, offset: int = 0) -> list[Email]
```

## Parameters

- `self`
- `filters` (`SearchFilters`)
- `account_id` (`str | None`)
- `limit`
- `offset` (`int`)

## Returns

`list[Email]`

## Calls

- [[backend.app.db.search_query.compile_fts_match|compile_fts_match]] (calls)
- `model_validate_json` (`backend.app.schemas.Email.model_validate_json`, calls-inferred)
- `getLogger` (`logging.getLogger`, calls-inferred)

## Reads

- [[table_emails]]
- [[table_emails_fts]]

## Side Effects

- SQLite
