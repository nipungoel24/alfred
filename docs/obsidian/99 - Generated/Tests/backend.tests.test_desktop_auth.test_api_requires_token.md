---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_desktop_auth
qualified_name: backend.tests.test_desktop_auth.test_api_requires_token
source: backend/tests/test_desktop_auth.py
line: 29
status: active
tags: [test, function, test]
---

# test_api_requires_token

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_api_requires_token` in `backend/tests/test_desktop_auth.py`.

## Location

`backend/tests/test_desktop_auth.py:29`

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
