---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_desktop_auth
qualified_name: backend.tests.test_desktop_auth.test_preflight_exemption_does_not_open_actual_requests
source: backend/tests/test_desktop_auth.py
line: 153
status: active
tags: [test, function, test]
---

# test_preflight_exemption_does_not_open_actual_requests

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Passing OPTIONS through must not weaken token enforcement on GET.

## Location

`backend/tests/test_desktop_auth.py:153`

## Signature

```python
(authed_app)
```

## Parameters

- `authed_app`

## Calls

- `TestClient` (`fastapi.testclient.TestClient`, calls-inferred)

## Side Effects

- network (HTTP)
