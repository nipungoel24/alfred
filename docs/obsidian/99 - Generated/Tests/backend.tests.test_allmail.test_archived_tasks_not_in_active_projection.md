---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_allmail
qualified_name: backend.tests.test_allmail.test_archived_tasks_not_in_active_projection
source: backend/tests/test_allmail.py
line: 165
status: active
tags: [test, function, test]
---

# test_archived_tasks_not_in_active_projection

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_archived_tasks_not_in_active_projection` in `backend/tests/test_allmail.py`.

## Location

`backend/tests/test_allmail.py:165`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.active_tasks|active_tasks]] (calls)
- [[backend.app.db.repositories.Repository.save_tasks_batch|save_tasks_batch]] (calls)
- [[backend.app.db.repositories.Repository.tasks|tasks]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)

## Reads

- [[table_emails]]
- [[table_tasks]]

## Writes

- [[table_emails]]
- [[table_tasks]]

## Side Effects

- SQLite
