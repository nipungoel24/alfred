---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_eligibility
qualified_name: backend.tests.test_eligibility.test_category_counts_derive_from_labels
source: backend/tests/test_eligibility.py
line: 238
status: active
tags: [test, function, test]
---

# test_category_counts_derive_from_labels

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_category_counts_derive_from_labels` in `backend/tests/test_eligibility.py`.

## Location

`backend/tests/test_eligibility.py:238`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.email_counts|email_counts]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)

## Reads

- [[table_emails]]

## Writes

- [[table_emails]]

## Side Effects

- SQLite
