---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.search_emails_structured
source: backend/app/main.py
line: 985
status: active
tags: [backend, function, endpoint]
---

# search_emails_structured

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Structured search with filters applied at the database level.

## Route

`POST /api/emails/search`

## Location

`backend/app/main.py:985`

## Signature

```python
(filters: SearchFilters, account_id: str | None = None, limit: int = 200, offset: int = 0)
```

## Parameters

- `filters` (`SearchFilters`)
- `account_id` (`str | None`)
- `limit` (`int`)
- `offset` (`int`)

## Calls

- [[backend.app.mail.fingerprint.content_fingerprint|content_fingerprint]] (calls)

## Side Effects

- none statically observed
