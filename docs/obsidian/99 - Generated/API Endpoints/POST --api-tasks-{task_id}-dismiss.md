---
type: endpoint
generated: true
layer: backend
qualified_name: backend.app.main.dismiss_task
source: backend/app/main.py
line: 1146
status: active
tags: [backend, function, endpoint, endpoint]
---

# POST /api/tasks/{task_id}/dismiss

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Durable "Not a task": hides the task and suppresses re-derivation.

## Handler

[[backend.app.main.dismiss_task|dismiss_task]]

## Location

`backend/app/main.py:1146`

## Parameters

- `task_id` (`str`)
