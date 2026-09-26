---
type: function
generated: true
language: python
layer: database
module: backend.app.db.secure_store
qualified_name: backend.app.db.secure_store.status
source: backend/app/db/secure_store.py
line: 127
status: active
tags: [database, function]
---

# status

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

A single word describing the credential store, for `/health`.

## Location

`backend/app/db/secure_store.py:127`

## Signature

```python
() -> str
```

## Returns

`str`

## Called By

- [[backend.app.main.health|health]]
- [[backend.tests.test_secure_store.TestFailClosed.test_status_reports_unavailable_when_dpapi_is_missing|test_status_reports_unavailable_when_dpapi_is_missing]]
- [[backend.tests.test_secure_store.TestHealthReporting.test_health_reports_a_single_known_state|test_health_reports_a_single_known_state]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_availability_probe_succeeds_on_windows|test_availability_probe_succeeds_on_windows]]

## Side Effects

- handles credentials/tokens — see [[Token Security]]
