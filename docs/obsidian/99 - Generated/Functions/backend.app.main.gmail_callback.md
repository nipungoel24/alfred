---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.gmail_callback
source: backend/app/main.py
line: 612
status: active
tags: [backend, function, endpoint]
---

# gmail_callback

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `gmail_callback` in `backend/app/main.py`.

## Route

`GET /api/accounts/gmail/callback`

## Location

`backend/app/main.py:612`

## Signature

```python
(code: str | None = Query(None), state: str | None = Query(None), redirect_uri: str | None = Query(None), error: str | None = Query(None))
```

## Parameters

- `code` (`str | None`)
- `state` (`str | None`)
- `redirect_uri` (`str | None`)
- `error` (`str | None`)

## Calls

- [[backend.app.db.secure_store.encrypt_token|encrypt_token]] (calls)
- [[backend.app.schemas.EmailAccount|EmailAccount]] (calls)
- `now` (`datetime.datetime.now`, calls-inferred)
- `timedelta` (`datetime.timedelta`, calls-inferred)

## Side Effects

- async I/O; handles credentials/tokens — see [[Token Security]]

## Security

See [[OAuth Security]] and [[Token Security]].
