---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_thread_isolation
qualified_name: backend.tests.test_thread_isolation.test_task_fingerprint_dual_form_dedupe
source: backend/tests/test_thread_isolation.py
line: 196
status: active
tags: [test, function, test]
---

# test_task_fingerprint_dual_form_dedupe

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Post-migration derivation must not duplicate pre-migration tasks.

## Location

`backend/tests/test_thread_isolation.py:196`

## Signature

```python
()
```

## Calls

- [[backend.app.mail.identity.scoped_thread_id|scoped_thread_id]] (calls)
- [[backend.app.services.task_derivation._normalize_action|_normalize_action]] (calls)
- [[backend.app.services.task_derivation.candidate_fingerprints|candidate_fingerprints]] (calls)
- [[backend.app.services.task_derivation.task_fingerprint|task_fingerprint]] (calls)

## Side Effects

- none statically observed
