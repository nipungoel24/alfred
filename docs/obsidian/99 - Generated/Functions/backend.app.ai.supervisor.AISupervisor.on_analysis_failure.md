---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.supervisor.AISupervisor
qualified_name: backend.app.ai.supervisor.AISupervisor.on_analysis_failure
source: backend/app/ai/supervisor.py
line: 515
status: active
tags: [ai, function]
---

# on_analysis_failure

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Classify a mid-analysis failure and update state.

## Location

`backend/app/ai/supervisor.py:515`

## Signature

```python
(self, exc: Exception) -> dict
```

## Parameters

- `self`
- `exc` (`Exception`)

## Returns

`dict`

## Side Effects

- async I/O
