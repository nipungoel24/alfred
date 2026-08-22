---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main._startup_background
source: backend/app/main.py
line: 391
status: active
tags: [backend, function]
---

# _startup_background

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Slow startup work that must NOT block /health readiness.

## Location

`backend/app/main.py:391`

## Signature

```python
()
```

## Calls

- [[backend.app.mail.backfill.normalize_cursor|normalize_cursor]] (calls)
- [[backend.app.services.task_derivation.rebuild_tasks_from_analyses|rebuild_tasks_from_analyses]] (calls)

## Writes

- [[table_jobs]]

## Side Effects

- async I/O; SQLite
