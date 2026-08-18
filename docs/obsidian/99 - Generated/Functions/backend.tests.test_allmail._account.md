---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_allmail
qualified_name: backend.tests.test_allmail._account
source: backend/tests/test_allmail.py
line: 206
status: active
tags: [test, function]
---

# _account

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `_account` in `backend/tests/test_allmail.py`.

## Location

`backend/tests/test_allmail.py:206`

## Signature

```python
(repo, cursor = None)
```

## Parameters

- `repo`
- `cursor`

## Calls

- [[backend.app.db.repositories.Repository.save_account|save_account]] (calls)
- [[backend.app.schemas.EmailAccount|EmailAccount]] (calls)

## Writes

- [[table_accounts]]

## Side Effects

- SQLite
