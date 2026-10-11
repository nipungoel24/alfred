---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.ai_model_select
source: backend/app/main.py
line: 1038
status: active
tags: [backend, function, endpoint]
---

# ai_model_select

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Select the model Alfred analyses with (Settings, criterion 2.7).

## Route

`POST /api/ai/model`

## Location

`backend/app/main.py:1038`

## Signature

```python
(body: ModelSelectRequest)
```

## Parameters

- `body` (`ModelSelectRequest`)

## Calls

- `HTTPException` (`fastapi.HTTPException`, calls-inferred)

## Side Effects

- async I/O
