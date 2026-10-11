---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.ai_model
source: backend/app/main.py
line: 997
status: active
tags: [backend, function, endpoint]
---

# ai_model

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

The configured model, the models really installed, and a preflight.

## Route

`GET /api/ai/model`

## Location

`backend/app/main.py:997`

## Signature

```python
()
```

## Calls

- [[backend.app.ai.resources.check_for_model_download|check_for_model_download]] (calls)
- [[backend.app.ai.resources.human_bytes|human_bytes]] (calls)

## Side Effects

- async I/O
