---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_eligibility
qualified_name: backend.tests.test_eligibility.test_permanent_delete_marks_excluded_not_destroyed
source: backend/tests/test_eligibility.py
line: 306
status: active
tags: [test, function, test]
---

# test_permanent_delete_marks_excluded_not_destroyed

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_permanent_delete_marks_excluded_not_destroyed` in `backend/tests/test_eligibility.py`.

## Location

`backend/tests/test_eligibility.py:306`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.email|email]] (calls)
- [[backend.app.db.repositories.Repository.email_eligibility|email_eligibility]] (calls)
- [[backend.app.db.repositories.Repository.mark_email_excluded|mark_email_excluded]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)

## Reads

- [[table_emails]]

## Writes

- [[table_emails]]

## Side Effects

- SQLite
