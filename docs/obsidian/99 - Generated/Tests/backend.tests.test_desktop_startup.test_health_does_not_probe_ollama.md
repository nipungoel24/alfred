---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_desktop_startup
qualified_name: backend.tests.test_desktop_startup.test_health_does_not_probe_ollama
source: backend/tests/test_desktop_startup.py
line: 61
status: active
tags: [test, function, test]
---

# test_health_does_not_probe_ollama

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Backend readiness is not AI readiness.

## Location

`backend/tests/test_desktop_startup.py:61`

## Signature

```python
(startup_app, monkeypatch)
```

## Parameters

- `startup_app`
- `monkeypatch`

## Calls

- `TestClient` (`fastapi.testclient.TestClient`, calls-inferred)

## Side Effects

- network (HTTP)
