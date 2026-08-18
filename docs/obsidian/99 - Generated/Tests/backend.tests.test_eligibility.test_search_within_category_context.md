---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_eligibility
qualified_name: backend.tests.test_eligibility.test_search_within_category_context
source: backend/tests/test_eligibility.py
line: 269
status: active
tags: [test, function, test]
---

# test_search_within_category_context

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_search_within_category_context` in `backend/tests/test_eligibility.py`.

## Location

`backend/tests/test_eligibility.py:269`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.emails_filtered|emails_filtered]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)
- [[backend.app.schemas.Email|Email]] (calls)

## Reads

- [[table_emails]]

## Writes

- [[table_emails]]

## Side Effects

- SQLite
