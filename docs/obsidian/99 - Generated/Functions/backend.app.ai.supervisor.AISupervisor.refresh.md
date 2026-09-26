---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.supervisor.AISupervisor
qualified_name: backend.app.ai.supervisor.AISupervisor.refresh
source: backend/app/ai/supervisor.py
line: 151
status: active
tags: [ai, function]
---

# refresh

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Run a full health check and update the state machine.

## Location

`backend/app/ai/supervisor.py:151`

## Signature

```python
(self, allow_auto_start: bool = True) -> dict
```

## Parameters

- `self`
- `allow_auto_start` (`bool`)

## Returns

`dict`

## Side Effects

- async I/O
