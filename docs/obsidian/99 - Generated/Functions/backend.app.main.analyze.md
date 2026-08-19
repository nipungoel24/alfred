---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.analyze
source: backend/app/main.py
line: 870
status: active
tags: [backend, function, endpoint]
---

# analyze

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `analyze` in `backend/app/main.py`.

## Route

`POST /api/emails/{email_id}/analyze`

## Location

`backend/app/main.py:870`

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

- async I/O
