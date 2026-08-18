---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_task_migration
source: backend/tests/test_task_migration.py
status: active
tags: [module, backend]
---

# backend.tests.test_task_migration

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_task_migration.py`

## Imports

- `ActionItem` ← `backend.app.schemas.ActionItem`
- `Category` ← `backend.app.schemas.Category`
- `Deadline` ← `backend.app.schemas.Deadline`
- `Email` ← `backend.app.schemas.Email`
- `EmailAccount` ← `backend.app.schemas.EmailAccount`
- `EmailAnalysis` ← `backend.app.schemas.EmailAnalysis`
- `Path` ← `pathlib.Path`
- `Priority` ← `backend.app.schemas.Priority`
- `Repository` ← `backend.app.db.repositories.Repository`
- `Task` ← `backend.app.schemas.Task`
- `TaskMigrationService` ← `backend.app.services.task_migration.TaskMigrationService`
- `datetime` ← `datetime.datetime`
- `json` ← `json`
- `os` ← `os`
- `pytest` ← `pytest`
- `sqlite3` ← `sqlite3`
- `tempfile` ← `tempfile`
- `timezone` ← `datetime.timezone`

## Functions

- [[backend.tests.test_task_migration.repo|repo]]
- [[backend.tests.test_task_migration.temp_db|temp_db]]
- [[backend.tests.test_task_migration.test_migration_rollback.crashing_analyses|crashing_analyses]]

## Tests

- [[backend.tests.test_task_migration.test_migration_idempotency_and_preservation|test_migration_idempotency_and_preservation]]
- [[backend.tests.test_task_migration.test_migration_rollback|test_migration_rollback]]
