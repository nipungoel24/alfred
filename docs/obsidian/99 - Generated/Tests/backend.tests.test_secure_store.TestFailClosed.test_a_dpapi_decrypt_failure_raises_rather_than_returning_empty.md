---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_secure_store.TestFailClosed
qualified_name: backend.tests.test_secure_store.TestFailClosed.test_a_dpapi_decrypt_failure_raises_rather_than_returning_empty
source: backend/tests/test_secure_store.py
line: 99
status: active
tags: [test, function, test]
---

# test_a_dpapi_decrypt_failure_raises_rather_than_returning_empty

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_a_dpapi_decrypt_failure_raises_rather_than_returning_empty` in `backend/tests/test_secure_store.py`.

## Location

`backend/tests/test_secure_store.py:99`

## Signature

```python
(self, monkeypatch)
```

## Parameters

- `self`
- `monkeypatch`

## Calls

- [[backend.app.db.secure_store.decrypt_token|decrypt_token]] (calls)
- [[backend.app.db.secure_store.encrypt_token|encrypt_token]] (calls)
- `raises` (`pytest.raises`, calls-inferred)

## Side Effects

- handles credentials/tokens — see [[Token Security]]
