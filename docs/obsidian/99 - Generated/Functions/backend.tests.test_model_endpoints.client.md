---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_model_endpoints
qualified_name: backend.tests.test_model_endpoints.client
source: backend/tests/test_model_endpoints.py
line: 30
status: active
tags: [test, function]
---

# client

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

One client whose portal loop outlives each request.

## Location

`backend/tests/test_model_endpoints.py:30`

## Signature

```python
(monkeypatch, tmp_path)
```

## Parameters

- `monkeypatch`
- `tmp_path`

## Calls

- [[backend.app.db.repositories.Repository|Repository]] (calls)
- `TestClient` (`fastapi.testclient.TestClient`, calls-inferred)

## Side Effects

- network (HTTP)
