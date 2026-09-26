---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_secure_store.TestLegacyMigration
qualified_name: backend.tests.test_secure_store.TestLegacyMigration.test_a_legacy_value_can_be_re_encrypted
source: backend/tests/test_secure_store.py
line: 143
status: active
tags: [test, function, test]
---

# test_a_legacy_value_can_be_re_encrypted

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_a_legacy_value_can_be_re_encrypted` in `backend/tests/test_secure_store.py`.

## Location

`backend/tests/test_secure_store.py:143`

## Signature

```python
(self)
```

## Parameters

- `self`

## Calls

- [[backend.app.db.secure_store.decrypt_token|decrypt_token]] (calls)
- [[backend.app.db.secure_store.encrypt_token|encrypt_token]] (calls)
- `b64encode` (`base64.b64encode`, calls-inferred)

## Side Effects

- handles credentials/tokens — see [[Token Security]]
