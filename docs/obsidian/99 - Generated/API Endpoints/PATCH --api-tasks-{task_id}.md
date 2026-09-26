---
type: endpoint
generated: true
layer: backend
qualified_name: backend.app.main.patch_task
source: backend/app/main.py
line: 1159
status: active
tags: [backend, function, endpoint, endpoint]
---

# PATCH /api/tasks/{task_id}

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Explicit user priority edit (task only — never rewrites the source

## Handler

[[backend.app.main.patch_task|patch_task]]

## Location

`backend/app/main.py:1159`

## Parameters

- `task_id` (`str`)
- `patch` (`TaskPriorityPatch`)
