---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.patch_task
source: backend/app/main.py
line: 1307
status: active
tags: [backend, function, endpoint]
---

# patch_task

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Explicit user priority edit (task only — never rewrites the source

## Route

`PATCH /api/tasks/{task_id}`

## Location

`backend/app/main.py:1307`

## Signature

```python
(task_id: str, patch: TaskPriorityPatch)
```

## Parameters

- `task_id` (`str`)
- `patch` (`TaskPriorityPatch`)

## Calls

- `HTTPException` (`fastapi.HTTPException`, calls-inferred)

## Side Effects

- none statically observed
