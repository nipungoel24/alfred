---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.app.services.task_migration
source: backend/app/services/task_migration.py
status: active
tags: [module, backend]
---

# backend.app.services.task_migration

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/app/services/task_migration.py`

## Imports

- `DERIVATION_VERSION` ← `backend.app.services.task_derivation.DERIVATION_VERSION`
- `Email` ← `backend.app.schemas.Email`
- `EmailAnalysis` ← `backend.app.schemas.EmailAnalysis`
- `List` ← `typing.List`
- `Repository` ← `backend.app.db.repositories.Repository`
- `Set` ← `typing.Set`
- `Task` ← `backend.app.schemas.Task`
- `Tuple` ← `typing.Tuple`
- `derive_tasks` ← `backend.app.services.task_derivation.derive_tasks`

## Classes

- [[backend.app.services.task_migration.TaskMigrationService|TaskMigrationService]]

## Functions

- [[backend.app.services.task_migration.TaskMigrationService.__init__|__init__]]
- [[backend.app.services.task_migration.TaskMigrationService.run_migration|run_migration]]
