---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_model_endpoints
qualified_name: backend.tests.test_model_endpoints._wire
source: backend/tests/test_model_endpoints.py
line: 57
status: active
tags: [test, function]
---

# _wire

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Point the app's module singletons at fakes and return the supervisor.

## Location

`backend/tests/test_model_endpoints.py:57`

## Signature

```python
(monkeypatch, pull_client = None)
```

## Parameters

- `monkeypatch`
- `pull_client`

## Calls

- [[backend.app.ai.supervisor.AISupervisor|AISupervisor]] (calls)
- [[backend.tests.test_model_supervisor.FakePullClient|FakePullClient]] (calls)

## Side Effects

- none statically observed
