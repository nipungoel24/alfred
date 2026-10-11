---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.ollama_client.OllamaClient
qualified_name: backend.app.ai.ollama_client.OllamaClient.model_size
source: backend/app/ai/ollama_client.py
line: 256
status: active
tags: [ai, function]
---

# model_size

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Real on-disk size of a locally installed model, or None if absent.

## Location

`backend/app/ai/ollama_client.py:256`

## Signature

```python
(self, model: str) -> int | None
```

## Parameters

- `self`
- `model` (`str`)

## Returns

`int | None`

## Side Effects

- async I/O
