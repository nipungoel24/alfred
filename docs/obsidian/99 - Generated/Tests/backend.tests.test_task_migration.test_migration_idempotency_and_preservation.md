---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_task_migration
qualified_name: backend.tests.test_task_migration.test_migration_idempotency_and_preservation
source: backend/tests/test_task_migration.py
line: 28
status: active
tags: [test, function, test]
---

# test_migration_idempotency_and_preservation

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_migration_idempotency_and_preservation` in `backend/tests/test_task_migration.py`.

## Location

`backend/tests/test_task_migration.py:28`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.accounts|accounts]] (calls)
- `commit` (`backend.app.db.repositories.Repository.con.commit`, calls-inferred)
- `execute` (`backend.app.db.repositories.Repository.con.execute`, calls-inferred)
- [[backend.app.db.repositories.Repository.email_count|email_count]] (calls)
- [[backend.app.db.repositories.Repository.save_account|save_account]] (calls)
- [[backend.app.db.repositories.Repository.save_analysis|save_analysis]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email_commit|upsert_email_commit]] (calls)
- [[backend.app.schemas.ActionItem|ActionItem]] (calls)
- [[backend.app.schemas.Deadline|Deadline]] (calls)
- [[backend.app.schemas.Email|Email]] (calls)
- [[backend.app.schemas.EmailAccount|EmailAccount]] (calls)
- [[backend.app.schemas.EmailAnalysis|EmailAnalysis]] (calls)
- [[backend.app.services.task_migration.TaskMigrationService|TaskMigrationService]] (calls)
- `now` (`datetime.datetime.now`, calls-inferred)

## Reads

- [[table_accounts]]
- [[table_emails]]
- [[table_tasks]]

## Writes

- [[table_accounts]]
- [[table_email_analysis]]
- [[table_tasks]]

## Side Effects

- SQLite
