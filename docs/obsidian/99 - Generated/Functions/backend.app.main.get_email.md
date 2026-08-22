---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.get_email
source: backend/app/main.py
line: 857
status: active
tags: [backend, function, endpoint]
---

# get_email

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `get_email` in `backend/app/main.py`.

## Route

`GET /api/emails/{email_id}`

## Location

`backend/app/main.py:857`

## Signature

```python
(email_id: str)
```

## Parameters

- `email_id` (`str`)

## Calls

- [[backend.app.mail.fingerprint.content_fingerprint|content_fingerprint]] (calls)
- `JSONResponse` (`fastapi.responses.JSONResponse`, calls-inferred)

## Side Effects

- none statically observed
