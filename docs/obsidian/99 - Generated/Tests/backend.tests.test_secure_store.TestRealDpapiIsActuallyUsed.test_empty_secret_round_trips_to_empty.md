---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed
qualified_name: backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_empty_secret_round_trips_to_empty
source: backend/tests/test_secure_store.py
line: 62
status: active
tags: [test, function, test]
---

# test_empty_secret_round_trips_to_empty

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_empty_secret_round_trips_to_empty` in `backend/tests/test_secure_store.py`.

## Location

`backend/tests/test_secure_store.py:62`

## Signature

```python
(self)
```

## Parameters

- `self`

## Calls

- [[backend.app.db.secure_store.decrypt_token|decrypt_token]] (calls)
- [[backend.app.db.secure_store.encrypt_token|encrypt_token]] (calls)

## Side Effects

- handles credentials/tokens — see [[Token Security]]
