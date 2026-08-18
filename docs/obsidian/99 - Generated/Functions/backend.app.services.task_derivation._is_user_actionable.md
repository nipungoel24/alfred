---
type: function
generated: true
language: python
layer: backend
module: backend.app.services.task_derivation
qualified_name: backend.app.services.task_derivation._is_user_actionable
source: backend/app/services/task_derivation.py
line: 54
status: active
tags: [backend, function]
---

# _is_user_actionable

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Determine if an action item is genuinely assigned to the user.

## Location

`backend/app/services/task_derivation.py:54`

## Signature

```python
(item: ActionItem, email: Email, analysis: EmailAnalysis) -> bool
```

## Parameters

- `item` (`ActionItem`)
- `email` (`Email`)
- `analysis` (`EmailAnalysis`)

## Returns

`bool`

## Side Effects

- none statically observed
