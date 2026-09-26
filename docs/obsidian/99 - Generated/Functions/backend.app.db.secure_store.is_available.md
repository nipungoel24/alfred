---
type: function
generated: true
language: python
layer: database
module: backend.app.db.secure_store
qualified_name: backend.app.db.secure_store.is_available
source: backend/app/db/secure_store.py
line: 113
status: active
tags: [database, function]
---

# is_available

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

True when a credential can be protected on this machine right now.

## Location

`backend/app/db/secure_store.py:113`

## Signature

```python
() -> bool
```

## Returns

`bool`

## Called By

- [[backend.tests.test_secure_store.TestFailClosed.test_status_reports_unavailable_when_dpapi_is_missing|test_status_reports_unavailable_when_dpapi_is_missing]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_availability_probe_succeeds_on_windows|test_availability_probe_succeeds_on_windows]]

## Side Effects

- handles credentials/tokens — see [[Token Security]]
