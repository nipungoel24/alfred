---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_secure_store.TestFailClosed
qualified_name: backend.tests.test_secure_store.TestFailClosed.test_status_reports_unavailable_when_dpapi_is_missing
source: backend/tests/test_secure_store.py
line: 83
status: active
tags: [test, function, test]
---

# test_status_reports_unavailable_when_dpapi_is_missing

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_status_reports_unavailable_when_dpapi_is_missing` in `backend/tests/test_secure_store.py`.

## Location

`backend/tests/test_secure_store.py:83`

## Signature

```python
(self, monkeypatch)
```

## Parameters

- `self`
- `monkeypatch`

## Calls

- [[backend.app.db.secure_store.is_available|is_available]] (calls)
- [[backend.app.db.secure_store.status|status]] (calls)

## Side Effects

- handles credentials/tokens — see [[Token Security]]
