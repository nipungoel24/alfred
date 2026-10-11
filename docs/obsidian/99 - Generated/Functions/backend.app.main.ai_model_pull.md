---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.ai_model_pull
source: backend/app/main.py
line: 1060
status: active
tags: [backend, function, endpoint]
---

# ai_model_pull

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Start downloading a model. Idempotent — returns live progress.

## Route

`POST /api/ai/model/pull`

## Location

`backend/app/main.py:1060`

## Signature

```python
(body: ModelPullRequest | None = None)
```

## Parameters

- `body` (`ModelPullRequest | None`)

## Calls

- `HTTPException` (`fastapi.HTTPException`, calls-inferred)

## Side Effects

- async I/O
