---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.save_tasks_batch
source: backend/app/db/repositories.py
line: 518
status: active
tags: [database, function]
---

# save_tasks_batch

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Save multiple tasks in a single transaction.

## Location

`backend/app/db/repositories.py:518`

## Signature

```python
(self, tasks_list: list[Task])
```

## Parameters

- `self`
- `tasks_list` (`list[Task]`)

## Calls

- [[backend.app.db.database.transaction|transaction]] (calls)
- `now` (`datetime.datetime.now`, calls-inferred)

## Called By

- [[backend.app.services.task_derivation.rebuild_tasks_from_analyses|rebuild_tasks_from_analyses]]
- [[backend.tests.test_allmail.test_archived_tasks_not_in_active_projection|test_archived_tasks_not_in_active_projection]]
- [[backend.tests.test_eligibility.test_active_tasks_exclude_spam_sourced|test_active_tasks_exclude_spam_sourced]]

## Writes

- [[table_tasks]]

## Side Effects

- SQLite
