---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_secure_store.TestLegacyMigration
qualified_name: backend.tests.test_secure_store.TestLegacyMigration.test_legacy_value_is_flagged_as_a_security_event
source: backend/tests/test_secure_store.py
line: 119
status: active
tags: [test, function, test]
---

# test_legacy_value_is_flagged_as_a_security_event

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_legacy_value_is_flagged_as_a_security_event` in `backend/tests/test_secure_store.py`.

## Location

`backend/tests/test_secure_store.py:119`

## Signature

```python
(self, caplog)
```

## Parameters

- `self`
- `caplog`

## Calls

- [[backend.app.db.secure_store.decrypt_token|decrypt_token]] (calls)
- `b64encode` (`base64.b64encode`, calls-inferred)

## Side Effects

- handles credentials/tokens — see [[Token Security]]
