---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_model_endpoints
qualified_name: backend.tests.test_model_endpoints._await_pull
source: backend/tests/test_model_endpoints.py
line: 72
status: active
tags: [test, function]
---

# _await_pull

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Wait for a download to settle, without touching its event loop.

## Location

`backend/tests/test_model_endpoints.py:72`

## Signature

```python
(client, sup, timeout = 5.0)
```

## Parameters

- `client`
- `sup`
- `timeout`

## Calls

- `sleep` (`time.sleep`, calls-inferred)
- `time` (`time.time`, calls-inferred)

## Side Effects

- none statically observed
