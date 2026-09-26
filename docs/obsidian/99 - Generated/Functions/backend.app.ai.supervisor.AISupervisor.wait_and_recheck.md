---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.supervisor.AISupervisor
qualified_name: backend.app.ai.supervisor.AISupervisor.wait_and_recheck
source: backend/app/ai/supervisor.py
line: 297
status: active
tags: [ai, function]
---

# wait_and_recheck

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Sleep the bounded backoff, then refresh health.

## Location

`backend/app/ai/supervisor.py:297`

## Signature

```python
(self) -> dict
```

## Parameters

- `self`

## Returns

`dict`

## Calls

- `sleep` (`asyncio.sleep`, calls-inferred)

## Side Effects

- async I/O
