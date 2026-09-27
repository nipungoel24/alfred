---
type: function
generated: true
language: python
layer: backend
module: backend.app.services.task_derivation
qualified_name: backend.app.services.task_derivation.rebuild_tasks_from_analyses
source: backend/app/services/task_derivation.py
line: 270
status: active
tags: [backend, function]
---

# rebuild_tasks_from_analyses

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Rebuild all derived tasks from cached analyses using the current derivation logic.

## Location

`backend/app/services/task_derivation.py:270`

## Signature

```python
(repo, model: str)
```

## Parameters

- `repo`
- `model` (`str`)

## Calls

- [[backend.app.db.repositories.Repository.all_analyses_with_emails|all_analyses_with_emails]] (calls)
- [[backend.app.db.repositories.Repository.delete_tasks_by_derivation_version|delete_tasks_by_derivation_version]] (calls)
- [[backend.app.db.repositories.Repository.save_tasks_batch|save_tasks_batch]] (calls)
- [[backend.app.db.repositories.Repository.task_exists_by_fingerprint|task_exists_by_fingerprint]] (calls)

## Called By

- [[backend.app.main._startup_background|_startup_background]]
- [[backend.tests.test_task_user_corrections.test_derivation_never_overwrites_user_priority|test_derivation_never_overwrites_user_priority]]
- [[backend.tests.test_task_user_corrections.test_dismiss_hides_and_suppresses_rederivation|test_dismiss_hides_and_suppresses_rederivation]]

## Reads

- [[table_email_analysis]]
- [[table_emails]]
- [[table_tasks]]

## Writes

- [[table_tasks]]

## Side Effects

- SQLite
