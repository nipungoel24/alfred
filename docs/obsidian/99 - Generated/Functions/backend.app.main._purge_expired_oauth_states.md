---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main._purge_expired_oauth_states
source: backend/app/main.py
line: 66
status: active
tags: [backend, function]
---

# _purge_expired_oauth_states

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Drop states whose redemption window has closed.

## Location

`backend/app/main.py:66`

## Signature

```python
(now: float | None = None) -> None
```

## Parameters

- `now` (`float | None`)

## Returns

`None`

## Calls

- `time` (`time.time`, calls-inferred)

## Called By

- [[backend.tests.test_model_endpoints.test_an_abandoned_state_is_purged_once_the_ttl_passes|test_an_abandoned_state_is_purged_once_the_ttl_passes]]
- [[backend.tests.test_model_endpoints.test_purging_keeps_concurrent_recent_flows_alive|test_purging_keeps_concurrent_recent_flows_alive]]

## Side Effects

- none statically observed
