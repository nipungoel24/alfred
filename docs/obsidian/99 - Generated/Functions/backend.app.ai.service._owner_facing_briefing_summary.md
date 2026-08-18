---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.service
qualified_name: backend.app.ai.service._owner_facing_briefing_summary
source: backend/app/ai/service.py
line: 95
status: active
tags: [ai, function]
---

# _owner_facing_briefing_summary

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Produce a factual fallback when a small local model describes its input instead of the inbox.

## Location

`backend/app/ai/service.py:95`

## Signature

```python
(urgent: int, high: int, reply: int, deadline_count: int) -> str
```

## Parameters

- `urgent` (`int`)
- `high` (`int`)
- `reply` (`int`)
- `deadline_count` (`int`)

## Returns

`str`

## Side Effects

- none statically observed
