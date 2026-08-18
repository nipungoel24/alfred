---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_eligibility
qualified_name: backend.tests.test_eligibility.test_active_tasks_exclude_spam_sourced
source: backend/tests/test_eligibility.py
line: 290
status: active
tags: [test, function, test]
---

# test_active_tasks_exclude_spam_sourced

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_active_tasks_exclude_spam_sourced` in `backend/tests/test_eligibility.py`.

## Location

`backend/tests/test_eligibility.py:290`

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
