---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_desktop_auth
qualified_name: backend.tests.test_desktop_auth.test_no_token_means_no_auth
source: backend/tests/test_desktop_auth.py
line: 64
status: active
tags: [test, function, test]
---

# test_no_token_means_no_auth

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Dev mode: without ALFRED_RUNTIME_TOKEN the API stays open.

## Location

`backend/tests/test_desktop_auth.py:64`

## Signature

```python
(tmp_path, monkeypatch)
```

## Parameters

- `tmp_path`
- `monkeypatch`

## Calls

- `TestClient` (`fastapi.testclient.TestClient`, calls-inferred)

## Side Effects

- network (HTTP); handles credentials/tokens — see [[Token Security]]
