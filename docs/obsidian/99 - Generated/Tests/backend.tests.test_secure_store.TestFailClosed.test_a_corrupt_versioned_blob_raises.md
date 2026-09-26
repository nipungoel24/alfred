---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_secure_store.TestFailClosed
qualified_name: backend.tests.test_secure_store.TestFailClosed.test_a_corrupt_versioned_blob_raises
source: backend/tests/test_secure_store.py
line: 107
status: active
tags: [test, function, test]
---

# test_a_corrupt_versioned_blob_raises

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_a_corrupt_versioned_blob_raises` in `backend/tests/test_secure_store.py`.

## Location

`backend/tests/test_secure_store.py:107`

## Signature

```python
(self)
```

## Parameters

- `self`

## Calls

- [[backend.app.db.secure_store.decrypt_token|decrypt_token]] (calls)
- `raises` (`pytest.raises`, calls-inferred)

## Side Effects

- handles credentials/tokens — see [[Token Security]]
