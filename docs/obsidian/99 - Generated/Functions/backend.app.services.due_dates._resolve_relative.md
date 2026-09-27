---
type: function
generated: true
language: python
layer: backend
module: backend.app.services.due_dates
qualified_name: backend.app.services.due_dates._resolve_relative
source: backend/app/services/due_dates.py
line: 289
status: active
tags: [backend, function]
---

# _resolve_relative

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Resolve "in 2 days" / "15 minutes from now" against a reference.

## Location

`backend/app/services/due_dates.py:289`

## Signature

```python
(text: str, reference: datetime | None) -> str | None
```

## Parameters

- `text` (`str`)
- `reference` (`datetime | None`)

## Returns

`str | None`

## Calls

- `timedelta` (`datetime.timedelta`, calls-inferred)

## Side Effects

- none statically observed
