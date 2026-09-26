---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_multi_account
qualified_name: backend.tests.test_multi_account.test_account_id_stored_correctly
source: backend/tests/test_multi_account.py
line: 32
status: active
tags: [test, function, test]
---

# test_account_id_stored_correctly

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Email account_id should be stored and retrieved correctly.

## Location

`backend/tests/test_multi_account.py:32`

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
