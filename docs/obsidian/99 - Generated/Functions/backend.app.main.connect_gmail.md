---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.connect_gmail
source: backend/app/main.py
line: 578
status: active
tags: [backend, function, endpoint]
---

# connect_gmail

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `connect_gmail` in `backend/app/main.py`.

## Route

`POST /api/accounts/gmail/connect`

## Location

`backend/app/main.py:578`

## Signature

```python
(redirect_uri: str = Query(...))
```

## Parameters

- `redirect_uri` (`str`)

## Calls

- `HTTPException` (`fastapi.HTTPException`, calls-inferred)
- `uuid4` (`uuid.uuid4`, calls-inferred)

## Side Effects

- async I/O; handles credentials/tokens — see [[Token Security]]

## Security

See [[OAuth Security]] and [[Token Security]].
