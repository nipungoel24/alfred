---
type: function
generated: true
language: python
layer: backend
module: backend.app.schemas
qualified_name: backend.app.schemas._clean_due
source: backend/app/schemas.py
line: 9
status: active
tags: [backend, function]
---

# _clean_due

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Reduce a model-supplied due value to a stored instant, or keep a

## Location

`backend/app/schemas.py:9`

## Signature

```python
(value: object) -> str | None
```

## Parameters

- `value` (`object`)

## Returns

`str | None`

## Calls

- [[backend.app.services.due_dates.is_relative_expression|is_relative_expression]] (calls)
- [[backend.app.services.due_dates.normalize_due_at|normalize_due_at]] (calls)

## Side Effects

- none statically observed
