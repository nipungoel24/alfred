---
type: function
generated: true
language: python
layer: backend
module: backend.app.services.due_dates
qualified_name: backend.app.services.due_dates._resolve_calendar
source: backend/app/services/due_dates.py
line: 239
status: active
tags: [backend, function]
---

# _resolve_calendar

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Resolve an explicit calendar date in `text` to an ISO date.

## Location

`backend/app/services/due_dates.py:239`

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

- `fromisoformat` (`datetime.datetime.fromisoformat`, calls-inferred)
- `search` (`re.search`, calls-inferred)

## Side Effects

- none statically observed
