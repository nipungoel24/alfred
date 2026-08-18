---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.get_emails
source: backend/app/main.py
line: 762
status: active
tags: [backend, function, endpoint]
---

# get_emails

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `get_emails` in `backend/app/main.py`.

## Route

`GET /api/emails`

## Location

`backend/app/main.py:762`

## Signature

```python
(q: str | None = None, priority: str | None = None, needs_reply: bool | None = None, account_id: str | None = None, category: str | None = None, scope: str = 'inbox', kind: str | None = None, limit: int = 200, offset: int = 0)
```

## Parameters

- `q` (`str | None`)
- `priority` (`str | None`)
- `needs_reply` (`bool | None`)
- `account_id` (`str | None`)
- `category` (`str | None`)
- `scope` (`str`)
- `kind` (`str | None`)
- `limit` (`int`)
- `offset` (`int`)

## Calls

- [[backend.app.mail.fingerprint.content_fingerprint|content_fingerprint]] (calls)
- `HTTPException` (`fastapi.HTTPException`, calls-inferred)

## Side Effects

- none statically observed
