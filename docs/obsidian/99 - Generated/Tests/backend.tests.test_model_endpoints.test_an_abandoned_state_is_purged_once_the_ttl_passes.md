---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_model_endpoints
qualified_name: backend.tests.test_model_endpoints.test_an_abandoned_state_is_purged_once_the_ttl_passes
source: backend/tests/test_model_endpoints.py
line: 104
status: active
tags: [test, function, test]
---

# test_an_abandoned_state_is_purged_once_the_ttl_passes

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_an_abandoned_state_is_purged_once_the_ttl_passes` in `backend/tests/test_model_endpoints.py`.

## Location

`backend/tests/test_model_endpoints.py:104`

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
