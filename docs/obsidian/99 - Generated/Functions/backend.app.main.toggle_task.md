---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.toggle_task
source: backend/app/main.py
line: 961
status: active
tags: [backend, function, endpoint]
---

# toggle_task

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `toggle_task` in `backend/app/main.py`.

## Route

`POST /api/tasks/{task_id}/toggle`

## Location

`backend/app/main.py:961`

## Signature

```python
(task_id: str)
```

## Parameters

- `task_id` (`str`)

## Calls

- `HTTPException` (`fastapi.HTTPException`, calls-inferred)

## Side Effects

- none statically observed
