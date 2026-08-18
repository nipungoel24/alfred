---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_task_derivation
source: backend/tests/test_task_derivation.py
status: active
tags: [module, backend]
---

# backend.tests.test_task_derivation

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_task_derivation.py`

## Imports

- `ActionItem` ← `backend.app.schemas.ActionItem`
- `Category` ← `backend.app.schemas.Category`
- `Deadline` ← `backend.app.schemas.Deadline`
- `Email` ← `backend.app.schemas.Email`
- `EmailAnalysis` ← `backend.app.schemas.EmailAnalysis`
- `Priority` ← `backend.app.schemas.Priority`
- `_is_noise` ← `backend.app.services.task_derivation._is_noise`
- `derive_tasks` ← `backend.app.services.task_derivation.derive_tasks`
- `pytest` ← `pytest`
- `task_fingerprint` ← `backend.app.services.task_derivation.task_fingerprint`

## Tests

- [[backend.tests.test_task_derivation.test_derive_tasks_adds_explicit_deadlines|test_derive_tasks_adds_explicit_deadlines]]
- [[backend.tests.test_task_derivation.test_derive_tasks_deduplicates_by_fingerprint|test_derive_tasks_deduplicates_by_fingerprint]]
- [[backend.tests.test_task_derivation.test_derive_tasks_ignores_newsletters_unless_urgent|test_derive_tasks_ignores_newsletters_unless_urgent]]
- [[backend.tests.test_task_derivation.test_derive_tasks_ignores_noise|test_derive_tasks_ignores_noise]]
- [[backend.tests.test_task_derivation.test_derive_tasks_ignores_third_party_owner|test_derive_tasks_ignores_third_party_owner]]
- [[backend.tests.test_task_derivation.test_is_noise_filtering|test_is_noise_filtering]]
