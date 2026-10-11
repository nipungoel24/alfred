---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.supervisor.AISupervisor
qualified_name: backend.app.ai.supervisor.AISupervisor.start_pull
source: backend/app/ai/supervisor.py
line: 297
status: active
tags: [ai, function]
---

# start_pull

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Begin downloading the configured model. Idempotent.

## Location

`backend/app/ai/supervisor.py:297`

## Signature

```python
(self, model: str | None = None) -> dict
```

## Parameters

- `self`
- `model` (`str | None`)

## Returns

`dict`

## Calls

- `create_task` (`asyncio.create_task`, calls-inferred)

## Side Effects

- async I/O
