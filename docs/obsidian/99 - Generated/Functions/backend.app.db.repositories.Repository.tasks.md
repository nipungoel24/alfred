---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.tasks
source: backend/app/db/repositories.py
line: 539
status: active
tags: [database, function]
---

# tasks

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `tasks` in `backend/app/db/repositories.py`.

## Location

`backend/app/db/repositories.py:539`

## Signature

```python
(self, status = None)
```

## Parameters

- `self`
- `status`

## Called By

- [[backend.tests.test_allmail.test_archived_tasks_not_in_active_projection|test_archived_tasks_not_in_active_projection]]
- [[backend.tests.test_eligibility.test_active_tasks_exclude_spam_sourced|test_active_tasks_exclude_spam_sourced]]
- [[backend.tests.test_task_migration.test_migration_rollback|test_migration_rollback]]

## Reads

- [[table_tasks]]

## Side Effects

- SQLite
