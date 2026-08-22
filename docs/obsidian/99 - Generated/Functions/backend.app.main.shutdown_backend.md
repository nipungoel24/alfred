---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.shutdown_backend
source: backend/app/main.py
line: 502
status: active
tags: [backend, function, endpoint]
---

# shutdown_backend

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Graceful in-process shutdown requested by the desktop shell.

## Route

`POST /api/shutdown`

## Location

`backend/app/main.py:502`

## Signature

```python
(request: Request)
```

## Parameters

- `request` (`Request`)

## Calls

- `get_running_loop` (`asyncio.get_running_loop`, calls-inferred)

## Side Effects

- async I/O
