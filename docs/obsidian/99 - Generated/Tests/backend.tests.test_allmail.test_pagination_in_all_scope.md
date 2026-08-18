---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_allmail
qualified_name: backend.tests.test_allmail.test_pagination_in_all_scope
source: backend/tests/test_allmail.py
line: 132
status: active
tags: [test, function, test]
---

# test_pagination_in_all_scope

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_pagination_in_all_scope` in `backend/tests/test_allmail.py`.

## Location

`backend/tests/test_allmail.py:132`

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
