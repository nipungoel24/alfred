---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_desktop_auth
qualified_name: backend.tests.test_desktop_auth.test_cors_preflight_passes_without_token
source: backend/tests/test_desktop_auth.py
line: 95
status: active
tags: [test, function, test]
---

# test_cors_preflight_passes_without_token

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Browsers never attach the session token to CORS preflights.

## Location

`backend/tests/test_desktop_auth.py:95`

## Signature

```python
(authed_app)
```

## Parameters

- `authed_app`

## Calls

- `TestClient` (`fastapi.testclient.TestClient`, calls-inferred)

## Side Effects

- network (HTTP); handles credentials/tokens — see [[Token Security]]
