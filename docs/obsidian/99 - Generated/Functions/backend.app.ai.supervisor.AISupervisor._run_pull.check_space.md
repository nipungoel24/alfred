---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.supervisor.AISupervisor._run_pull
qualified_name: backend.app.ai.supervisor.AISupervisor._run_pull.check_space
source: backend/app/ai/supervisor.py
line: 371
status: active
tags: [ai, function]
---

# check_space

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `check_space` in `backend/app/ai/supervisor.py`.

## Location

`backend/app/ai/supervisor.py:371`

## Signature

```python
(total: int | None)
```

## Parameters

- `total` (`int | None`)

## Calls

- [[backend.app.ai.ollama_client.OllamaInsufficientSpace|OllamaInsufficientSpace]] (calls)
- [[backend.app.ai.resources.check_for_model_download|check_for_model_download]] (calls)

## Side Effects

- network (HTTP)
