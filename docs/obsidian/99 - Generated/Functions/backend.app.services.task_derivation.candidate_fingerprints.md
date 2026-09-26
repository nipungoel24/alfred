---
type: function
generated: true
language: python
layer: backend
module: backend.app.services.task_derivation
qualified_name: backend.app.services.task_derivation.candidate_fingerprints
source: backend/app/services/task_derivation.py
line: 102
status: active
tags: [backend, function]
---

# candidate_fingerprints

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

All fingerprints under which a task for this action may be stored.

## Location

`backend/app/services/task_derivation.py:102`

## Signature

```python
(thread_id: str | None, account_id: str | None, normalized_action: str) -> list[str]
```

## Parameters

- `thread_id` (`str | None`)
- `account_id` (`str | None`)
- `normalized_action` (`str`)

## Returns

`list[str]`

## Called By

- [[backend.tests.test_thread_isolation.test_task_fingerprint_dual_form_dedupe|test_task_fingerprint_dual_form_dedupe]]

## Side Effects

- none statically observed
