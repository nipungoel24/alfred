---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_desktop_startup
qualified_name: backend.tests.test_desktop_startup.test_oauth_callback_exempt_under_token
source: backend/tests/test_desktop_startup.py
line: 61
status: active
tags: [test, function, test]
---

# test_oauth_callback_exempt_under_token

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_oauth_callback_exempt_under_token` in `backend/tests/test_desktop_startup.py`.

## Location

`backend/tests/test_desktop_startup.py:61`

## Signature

```python
(startup_app)
```

## Parameters

- `startup_app`

## Calls

- `TestClient` (`fastapi.testclient.TestClient`, calls-inferred)

## Side Effects

- network (HTTP); handles credentials/tokens — see [[Token Security]]
