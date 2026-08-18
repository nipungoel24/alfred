---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.ollama_client.OllamaClient
qualified_name: backend.app.ai.ollama_client.OllamaClient.__init__
source: backend/app/ai/ollama_client.py
line: 49
status: active
tags: [ai, function]
---

# __init__

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `__init__` in `backend/app/ai/ollama_client.py`.

## Location

`backend/app/ai/ollama_client.py:49`

## Signature

```python
(self, base_url: str, client: httpx.AsyncClient | None = None, default_timeout: float = 120.0, keep_alive: str = '30m')
```

## Parameters

- `self`
- `base_url` (`str`)
- `client` (`httpx.AsyncClient | None`)
- `default_timeout` (`float`)
- `keep_alive` (`str`)

## Calls

- `AsyncClient` (`httpx.AsyncClient`, calls-inferred)

## Side Effects

- none statically observed
