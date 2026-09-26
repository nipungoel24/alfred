---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.dismiss_task
source: backend/app/main.py
line: 1146
status: active
tags: [backend, function, endpoint]
---

# dismiss_task

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Durable "Not a task": hides the task and suppresses re-derivation.

## Route

`POST /api/tasks/{task_id}/dismiss`

## Location

`backend/app/main.py:1146`

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
