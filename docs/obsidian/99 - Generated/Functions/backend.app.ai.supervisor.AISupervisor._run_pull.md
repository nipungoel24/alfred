---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.supervisor.AISupervisor
qualified_name: backend.app.ai.supervisor.AISupervisor._run_pull
source: backend/app/ai/supervisor.py
line: 360
status: active
tags: [ai, function]
---

# _run_pull

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Download `model`, publishing real progress as it arrives.

## Location

`backend/app/ai/supervisor.py:360`

## Signature

```python
(self, model: str, generation: int, previous_state: str)
```

## Parameters

- `self`
- `model` (`str`)
- `generation` (`int`)
- `previous_state` (`str`)

## Calls

- [[backend.app.ai.ollama_client.OllamaInsufficientSpace|OllamaInsufficientSpace]] (calls)
- [[backend.app.ai.resources.check_for_model_download|check_for_model_download]] (calls)
- [[backend.app.ai.resources.human_bytes|human_bytes]] (calls)

## Side Effects

- async I/O; network (HTTP)
