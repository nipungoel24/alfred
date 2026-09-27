---
type: function
generated: true
language: python
layer: backend
module: backend.app.services.due_dates
qualified_name: backend.app.services.due_dates.is_non_action
source: backend/app/services/due_dates.py
line: 388
status: active
tags: [backend, function]
---

# is_non_action

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

True when `value` states that no action is required.

## Location

`backend/app/services/due_dates.py:388`

## Signature

```python
(value: object) -> bool
```

## Parameters

- `value` (`object`)

## Returns

`bool`

## Called By

- [[backend.app.services.task_derivation._is_user_actionable|_is_user_actionable]]
- [[backend.app.services.task_derivation.derive_tasks|derive_tasks]]

## Side Effects

- none statically observed
