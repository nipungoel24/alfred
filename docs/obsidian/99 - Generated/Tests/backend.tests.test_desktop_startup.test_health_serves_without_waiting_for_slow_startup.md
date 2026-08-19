---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_desktop_startup
qualified_name: backend.tests.test_desktop_startup.test_health_serves_without_waiting_for_slow_startup
source: backend/tests/test_desktop_startup.py
line: 32
status: active
tags: [test, function, test]
---

# test_health_serves_without_waiting_for_slow_startup

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

The desktop shell probes /health on a bounded timeout.

## Location

`backend/tests/test_desktop_startup.py:32`

## Signature

```python
(startup_app, monkeypatch)
```

## Parameters

- `startup_app`
- `monkeypatch`

## Calls

- `Event` (`asyncio.Event`, calls-inferred)
- `sleep` (`asyncio.sleep`, calls-inferred)
- `TestClient` (`fastapi.testclient.TestClient`, calls-inferred)
- `perf_counter` (`time.perf_counter`, calls-inferred)

## Side Effects

- network (HTTP)
