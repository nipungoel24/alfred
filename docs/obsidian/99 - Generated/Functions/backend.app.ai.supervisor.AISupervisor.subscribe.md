---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.supervisor.AISupervisor
qualified_name: backend.app.ai.supervisor.AISupervisor.subscribe
source: backend/app/ai/supervisor.py
line: 105
status: active
tags: [ai, function]
---

# subscribe

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Register a synchronous callback invoked on state changes.

## Location

`backend/app/ai/supervisor.py:105`

## Signature

```python
(self, callback: Callable[[str], None])
```

## Parameters

- `self`
- `callback` (`Callable[[str], None]`)

## Side Effects

- none statically observed
