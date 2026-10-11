---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.supervisor.AISupervisor
qualified_name: backend.app.ai.supervisor.AISupervisor._pull_owns_state
source: backend/app/ai/supervisor.py
line: 273
status: active
tags: [ai, function]
---

# _pull_owns_state

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

True when a download task is running and is not the caller.

## Location

`backend/app/ai/supervisor.py:273`

## Signature

```python
(self) -> bool
```

## Parameters

- `self`

## Returns

`bool`

## Calls

- `current_task` (`asyncio.current_task`, calls-inferred)

## Side Effects

- none statically observed
