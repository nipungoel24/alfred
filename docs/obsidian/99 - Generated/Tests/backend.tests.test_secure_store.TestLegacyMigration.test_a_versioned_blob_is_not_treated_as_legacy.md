---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_secure_store.TestLegacyMigration
qualified_name: backend.tests.test_secure_store.TestLegacyMigration.test_a_versioned_blob_is_not_treated_as_legacy
source: backend/tests/test_secure_store.py
line: 129
status: active
tags: [test, function, test]
---

# test_a_versioned_blob_is_not_treated_as_legacy

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_a_versioned_blob_is_not_treated_as_legacy` in `backend/tests/test_secure_store.py`.

## Location

`backend/tests/test_secure_store.py:129`

## Signature

```python
(self, caplog)
```

## Parameters

- `self`
- `caplog`

## Calls

- [[backend.app.db.secure_store.decrypt_token|decrypt_token]] (calls)
- [[backend.app.db.secure_store.encrypt_token|encrypt_token]] (calls)

## Side Effects

- handles credentials/tokens — see [[Token Security]]
