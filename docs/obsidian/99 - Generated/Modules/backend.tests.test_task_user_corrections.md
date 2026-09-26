---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_task_user_corrections
source: backend/tests/test_task_user_corrections.py
status: active
tags: [module, backend]
---

# backend.tests.test_task_user_corrections

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_task_user_corrections.py`

## Imports

- `Category` ← `backend.app.schemas.Category`
- `Email` ← `backend.app.schemas.Email`
- `EmailAnalysis` ← `backend.app.schemas.EmailAnalysis`
- `Priority` ← `backend.app.schemas.Priority`
- `Repository` ← `backend.app.db.repositories.Repository`
- `TestClient` ← `fastapi.testclient.TestClient`
- `pytest` ← `pytest`
- `rebuild_tasks_from_analyses` ← `backend.app.services.task_derivation.rebuild_tasks_from_analyses`

## Functions

- [[backend.tests.test_task_user_corrections._seed_derived|_seed_derived]]
- [[backend.tests.test_task_user_corrections.isolated_app|isolated_app]]

## Tests

- [[backend.tests.test_task_user_corrections.test_derivation_never_overwrites_user_priority|test_derivation_never_overwrites_user_priority]]
- [[backend.tests.test_task_user_corrections.test_dismiss_hides_and_suppresses_rederivation|test_dismiss_hides_and_suppresses_rederivation]]
- [[backend.tests.test_task_user_corrections.test_dismiss_unknown_task_404|test_dismiss_unknown_task_404]]
- [[backend.tests.test_task_user_corrections.test_dismissal_survives_reopen|test_dismissal_survives_reopen]]
- [[backend.tests.test_task_user_corrections.test_migration_service_never_revives_dismissed|test_migration_service_never_revives_dismissed]]
- [[backend.tests.test_task_user_corrections.test_migration_service_respects_override|test_migration_service_respects_override]]
- [[backend.tests.test_task_user_corrections.test_priority_patch_persists|test_priority_patch_persists]]
- [[backend.tests.test_task_user_corrections.test_priority_patch_rejects_invalid|test_priority_patch_rejects_invalid]]
- [[backend.tests.test_task_user_corrections.test_priority_patch_unknown_task_404|test_priority_patch_unknown_task_404]]
