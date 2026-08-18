---
type: function
generated: true
language: python
layer: backend
module: backend.app.services.task_derivation
qualified_name: backend.app.services.task_derivation._normalize_action
source: backend/app/services/task_derivation.py
line: 85
status: active
tags: [backend, function]
---

# _normalize_action

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Normalize action text for deduplication.

## Location

`backend/app/services/task_derivation.py:85`

## Signature

```python
(description: str) -> str
```

## Parameters

- `description` (`str`)

## Returns

`str`

## Calls

- `sub` (`re.sub`, calls-inferred)

## Side Effects

- none statically observed
