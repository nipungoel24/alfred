---
type: function
generated: true
language: python
layer: backend
module: backend.app.services.due_dates
qualified_name: backend.app.services.due_dates._iso_from_parts
source: backend/app/services/due_dates.py
line: 231
status: active
tags: [backend, function]
---

# _iso_from_parts

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

A calendar date becomes midnight UTC, so every value has one shape.

## Location

`backend/app/services/due_dates.py:231`

## Signature

```python
(year: int, month: int, day: int) -> str | None
```

## Parameters

- `year` (`int`)
- `month` (`int`)
- `day` (`int`)

## Returns

`str | None`

## Calls

- `datetime` (`datetime.datetime`, calls-inferred)

## Side Effects

- none statically observed
