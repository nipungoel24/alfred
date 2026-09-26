---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_thread_isolation
qualified_name: backend.tests.test_thread_isolation.test_draft_endpoint_isolation
source: backend/tests/test_thread_isolation.py
line: 104
status: active
tags: [test, function, test]
---

# test_draft_endpoint_isolation

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

The AI draft prompt for A must contain ONLY A's thread messages.

## Location

`backend/tests/test_thread_isolation.py:104`

## Signature

```python
(isolated_app, provider)
```

## Parameters

- `isolated_app`
- `provider`

## Calls

- `TestClient` (`fastapi.testclient.TestClient`, calls-inferred)

## Side Effects

- network (HTTP)
