---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.delete_tasks_by_derivation_version
source: backend/app/db/repositories.py
line: 595
status: active
tags: [database, function]
---

# delete_tasks_by_derivation_version

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Delete all tasks created by a specific derivation version.

## Location

`backend/app/db/repositories.py:595`

## Signature

```python
(self, version: str)
```

## Parameters

- `self`
- `version` (`str`)

## Called By

- [[backend.app.services.task_derivation.rebuild_tasks_from_analyses|rebuild_tasks_from_analyses]]

## Writes

- [[table_tasks]]

## Side Effects

- SQLite
