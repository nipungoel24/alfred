---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_desktop_auth
qualified_name: backend.tests.test_desktop_auth.test_unknown_origin_gets_no_cors_headers
source: backend/tests/test_desktop_auth.py
line: 141
status: active
tags: [test, function, test]
---

# test_unknown_origin_gets_no_cors_headers

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

CORS stays restrictive: unlisted origins must not receive ACAO.

## Location

`backend/tests/test_desktop_auth.py:141`

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
