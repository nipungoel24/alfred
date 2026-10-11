---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main._register_oauth_state
source: backend/app/main.py
line: 81
status: active
tags: [backend, function]
---

# _register_oauth_state

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Record a pending handshake under the size bound.

## Location

`backend/app/main.py:81`

## Signature

```python
(state: str, verifier: str, redirect_uri: str) -> None
```

## Parameters

- `state` (`str`)
- `verifier` (`str`)
- `redirect_uri` (`str`)

## Returns

`None`

## Calls

- `time` (`time.time`, calls-inferred)

## Called By

- [[backend.tests.test_model_endpoints.test_cap_eviction_drops_the_oldest_not_an_arbitrary_flow|test_cap_eviction_drops_the_oldest_not_an_arbitrary_flow]]
- [[backend.tests.test_model_endpoints.test_the_state_dict_never_exceeds_its_cap|test_the_state_dict_never_exceeds_its_cap]]

## Side Effects

- none statically observed
