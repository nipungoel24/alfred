---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_model_endpoints
qualified_name: backend.tests.test_model_endpoints.test_purging_keeps_concurrent_recent_flows_alive
source: backend/tests/test_model_endpoints.py
line: 155
status: active
tags: [test, function, test]
---

# test_purging_keeps_concurrent_recent_flows_alive

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_purging_keeps_concurrent_recent_flows_alive` in `backend/tests/test_model_endpoints.py`.

## Location

`backend/tests/test_model_endpoints.py:155`

## Signature

```python
(oauth_states)
```

## Parameters

- `oauth_states`

## Calls

- [[backend.app.main._purge_expired_oauth_states|_purge_expired_oauth_states]] (calls)
- `time` (`time.time`, calls-inferred)

## Side Effects

- none statically observed
