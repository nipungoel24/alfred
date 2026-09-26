---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed
qualified_name: backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_stored_blob_is_not_reversible_base64
source: backend/tests/test_secure_store.py
line: 37
status: active
tags: [test, function, test]
---

# test_stored_blob_is_not_reversible_base64

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_stored_blob_is_not_reversible_base64` in `backend/tests/test_secure_store.py`.

## Location

`backend/tests/test_secure_store.py:37`

## Signature

```python
(self)
```

## Parameters

- `self`

## Calls

- [[backend.app.db.secure_store.encrypt_token|encrypt_token]] (calls)
- `b64decode` (`base64.b64decode`, calls-inferred)
- `raises` (`pytest.raises`, calls-inferred)

## Side Effects

- handles credentials/tokens — see [[Token Security]]
