---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_secure_store.TestFailClosed
qualified_name: backend.tests.test_secure_store.TestFailClosed.test_no_credential_is_returned_when_storage_fails
source: backend/tests/test_secure_store.py
line: 78
status: active
tags: [test, function, test]
---

# test_no_credential_is_returned_when_storage_fails

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_no_credential_is_returned_when_storage_fails` in `backend/tests/test_secure_store.py`.

## Location

`backend/tests/test_secure_store.py:78`

## Signature

```python
(self, monkeypatch)
```

## Parameters

- `self`
- `monkeypatch`

## Calls

- [[backend.app.db.secure_store.encrypt_token|encrypt_token]] (calls)
- `raises` (`pytest.raises`, calls-inferred)

## Side Effects

- handles credentials/tokens — see [[Token Security]]
