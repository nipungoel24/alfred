---
type: function
generated: true
language: python
layer: backend
module: backend.app.services.task_derivation
qualified_name: backend.app.services.task_derivation.derive_tasks
source: backend/app/services/task_derivation.py
line: 119
status: active
tags: [backend, function, critical-path]
---

# derive_tasks

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Derive genuine user tasks from an email analysis.

## Location

`backend/app/services/task_derivation.py:119`

## Signature

```python
(email: Email, analysis: EmailAnalysis) -> list[Task]
```

## Parameters

- `email` (`Email`)
- `analysis` (`EmailAnalysis`)

## Returns

`list[Task]`

## Calls

- [[backend.app.schemas.Task|Task]] (calls)
- `now` (`datetime.datetime.now`, calls-inferred)

## Called By

- [[backend.app.main._derive_and_save_tasks|_derive_and_save_tasks]]
- [[backend.app.services.task_migration.TaskMigrationService.run_migration|run_migration]]
- [[backend.tests.test_task_derivation.test_derive_tasks_adds_explicit_deadlines|test_derive_tasks_adds_explicit_deadlines]]
- [[backend.tests.test_task_derivation.test_derive_tasks_deduplicates_by_fingerprint|test_derive_tasks_deduplicates_by_fingerprint]]
- [[backend.tests.test_task_derivation.test_derive_tasks_ignores_newsletters_unless_urgent|test_derive_tasks_ignores_newsletters_unless_urgent]]
- [[backend.tests.test_task_derivation.test_derive_tasks_ignores_noise|test_derive_tasks_ignores_noise]]
- [[backend.tests.test_task_derivation.test_derive_tasks_ignores_third_party_owner|test_derive_tasks_ignores_third_party_owner]]

## Side Effects

- none statically observed
