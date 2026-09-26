---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_multi_account
qualified_name: backend.tests.test_multi_account.test_delete_email_by_account
source: backend/tests/test_multi_account.py
line: 119
status: active
tags: [test, function, test]
---

# test_delete_email_by_account

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Deleting an email should only affect that email.

## Location

`backend/tests/test_multi_account.py:119`

## Signature

```python
(tmp_path: Path)
```

## Parameters

- `tmp_path` (`Path`)

## Calls

- [[backend.app.db.repositories.Repository|Repository]] (calls)

## Reads

- [[table_emails]]

## Side Effects

- SQLite
