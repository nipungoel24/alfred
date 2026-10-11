---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.ollama_client.OllamaClient
qualified_name: backend.app.ai.ollama_client.OllamaClient.pull_model
source: backend/app/ai/ollama_client.py
line: 270
status: active
tags: [ai, function]
---

# pull_model

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Download a model, streaming real per-layer byte progress.

## Location

`backend/app/ai/ollama_client.py:270`

## Signature

```python
(self, model: str, on_progress: Callable[[PullProgress], None] | None = None, check_space: Callable[[int | None], None] | None = None) -> PullProgress
```

## Parameters

- `self`
- `model` (`str`)
- `on_progress` (`Callable[[PullProgress], None] | None`)
- `check_space` (`Callable[[int | None], None] | None`)

## Returns

`PullProgress`

## Calls

- `Timeout` (`httpx.Timeout`, calls-inferred)

## Side Effects

- async I/O
