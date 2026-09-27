---
type: function
generated: true
language: python
layer: backend
module: backend.app.services.due_dates
qualified_name: backend.app.services.due_dates.is_relative_expression
source: backend/app/services/due_dates.py
line: 398
status: active
tags: [backend, function]
---

# is_relative_expression

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

True when `value` is a relative offset that a timestamp can resolve.

## Location

`backend/app/services/due_dates.py:398`

## Signature

```python
(value: object) -> bool
```

## Parameters

- `value` (`object`)

## Returns

`bool`

## Called By

- [[backend.app.schemas._clean_due|_clean_due]]

## Side Effects

- none statically observed
