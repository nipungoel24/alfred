---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_eligibility
qualified_name: backend.tests.test_eligibility.test_category_filter_is_db_driven
source: backend/tests/test_eligibility.py
line: 258
status: active
tags: [test, function, test]
---

# test_category_filter_is_db_driven

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_category_filter_is_db_driven` in `backend/tests/test_eligibility.py`.

## Location

`backend/tests/test_eligibility.py:258`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.emails_filtered|emails_filtered]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)

## Reads

- [[table_emails]]

## Writes

- [[table_emails]]

## Side Effects

- SQLite
