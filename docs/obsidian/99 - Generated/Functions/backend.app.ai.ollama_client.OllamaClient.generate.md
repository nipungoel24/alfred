---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.ollama_client.OllamaClient
qualified_name: backend.app.ai.ollama_client.OllamaClient.generate
source: backend/app/ai/ollama_client.py
line: 80
status: active
tags: [ai, function, critical-path]
---

# generate

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Generate a response from Ollama.

## Location

`backend/app/ai/ollama_client.py:80`

## Signature

```python
(self, model: str, prompt: str, schema = None, temperature: float = 0.0) -> tuple[str, InferenceMetrics]
```

## Parameters

- `self`
- `model` (`str`)
- `prompt` (`str`)
- `schema`
- `temperature` (`float`)

## Returns

`tuple[str, InferenceMetrics]`

## Calls

- `sub` (`re.sub`, calls-inferred)

## Side Effects

- async I/O
