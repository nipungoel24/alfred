---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.active_tasks
source: backend/app/db/repositories.py
line: 548
status: active
tags: [database, function]
---

# active_tasks

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Current-attention task projection.

## Location

`backend/app/db/repositories.py:548`

## Signature

```python
(self, status = None) -> list[Task]
```

## Parameters

- `self`
- `status`

## Returns

`list[Task]`

## Called By

- [[backend.tests.test_allmail.test_archived_tasks_not_in_active_projection|test_archived_tasks_not_in_active_projection]]
- [[backend.tests.test_eligibility.test_active_tasks_exclude_spam_sourced|test_active_tasks_exclude_spam_sourced]]

## Reads

- [[table_emails]]
- [[table_tasks]]

## Side Effects

- SQLite
