---
type: function
generated: true
language: python
layer: backend
module: backend.app.services.due_dates
qualified_name: backend.app.services.due_dates.is_temporal_only
source: backend/app/services/due_dates.py
line: 335
status: active
tags: [backend, function]
---

# is_temporal_only

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

True when `value` is nothing but a date/time expression.

## Location

`backend/app/services/due_dates.py:335`

## Signature

```python
(value: object) -> bool
```

## Parameters

- `value` (`object`)

## Returns

`bool`

## Calls

- `sub` (`re.sub`, calls-inferred)

## Called By

- [[backend.app.services.task_derivation._is_user_actionable|_is_user_actionable]]
- [[backend.app.services.task_derivation.derive_tasks|derive_tasks]]
- [[backend.tests.test_task_extraction_contract.test_non_action_titles_are_rejected|test_non_action_titles_are_rejected]]
- [[backend.tests.test_task_extraction_contract.test_real_action_titles_are_kept|test_real_action_titles_are_kept]]

## Side Effects

- none statically observed
