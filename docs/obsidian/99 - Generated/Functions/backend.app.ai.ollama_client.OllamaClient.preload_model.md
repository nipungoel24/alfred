---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.ollama_client.OllamaClient
qualified_name: backend.app.ai.ollama_client.OllamaClient.preload_model
source: backend/app/ai/ollama_client.py
line: 67
status: active
tags: [ai, function]
---

# preload_model

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Preload a model into VRAM/RAM to avoid cold-start latency on first inference.

## Location

`backend/app/ai/ollama_client.py:67`

## Signature

```python
(self, model: str)
```

## Parameters

- `self`
- `model` (`str`)

## Side Effects

- async I/O
