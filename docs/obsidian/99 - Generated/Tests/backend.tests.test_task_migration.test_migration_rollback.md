---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_task_migration
qualified_name: backend.tests.test_task_migration.test_migration_rollback
source: backend/tests/test_task_migration.py
line: 94
status: active
tags: [test, function, test]
---

# test_migration_rollback

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_migration_rollback` in `backend/tests/test_task_migration.py`.

## Location

`backend/tests/test_task_migration.py:94`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.save_analysis|save_analysis]] (calls)
- [[backend.app.db.repositories.Repository.tasks|tasks]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email_commit|upsert_email_commit]] (calls)
- [[backend.app.schemas.Email|Email]] (calls)
- [[backend.app.schemas.EmailAnalysis|EmailAnalysis]] (calls)
- [[backend.app.services.task_migration.TaskMigrationService|TaskMigrationService]] (calls)
- `now` (`datetime.datetime.now`, calls-inferred)
- `raises` (`pytest.raises`, calls-inferred)

## Reads

- [[table_tasks]]

## Writes

- [[table_email_analysis]]

## Side Effects

- SQLite
