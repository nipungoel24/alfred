---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_desktop_auth
qualified_name: backend.tests.test_desktop_auth.test_oauth_callback_is_exempt_from_token
source: backend/tests/test_desktop_auth.py
line: 64
status: active
tags: [test, function, test]
---

# test_oauth_callback_is_exempt_from_token

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

The system browser's OAuth redirect carries no session token — its

## Location

`backend/tests/test_desktop_auth.py:64`

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
