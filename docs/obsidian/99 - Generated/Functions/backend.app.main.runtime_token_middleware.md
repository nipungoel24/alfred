---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.runtime_token_middleware
source: backend/app/main.py
line: 464
status: active
tags: [backend, function]
---

# runtime_token_middleware

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `runtime_token_middleware` in `backend/app/main.py`.

## Location

`backend/app/main.py:464`

## Signature

```python
(request: Request, call_next)
```

## Parameters

- `request` (`Request`)
- `call_next`

## Calls

- `JSONResponse` (`fastapi.responses.JSONResponse`, calls-inferred)

## Side Effects

- async I/O; handles credentials/tokens — see [[Token Security]]
