---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.service
qualified_name: backend.app.ai.service._prepare_body
source: backend/app/ai/service.py
line: 49
status: active
tags: [ai, function]
---

# _prepare_body

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Prepare email body for analysis: truncate, strip quotes, strip noise.

## Location

`backend/app/ai/service.py:49`

## Signature

```python
(body: str) -> str
```

## Parameters

- `body` (`str`)

## Returns

`str`

## Calls

- `match` (`re.match`, calls-inferred)
- `sub` (`re.sub`, calls-inferred)

## Side Effects

- none statically observed
