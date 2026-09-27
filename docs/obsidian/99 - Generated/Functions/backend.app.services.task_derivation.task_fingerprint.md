---
type: function
generated: true
language: python
layer: backend
module: backend.app.services.task_derivation
qualified_name: backend.app.services.task_derivation.task_fingerprint
source: backend/app/services/task_derivation.py
line: 120
status: active
tags: [backend, function]
---

# task_fingerprint

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Create a stable fingerprint for task deduplication.

## Location

`backend/app/services/task_derivation.py:120`

## Signature

```python
(thread_id: str | None, normalized_action: str) -> str
```

## Parameters

- `thread_id` (`str | None`)
- `normalized_action` (`str`)

## Returns

`str`

## Calls

- `sha256` (`hashlib.sha256`, calls-inferred)

## Called By

- [[backend.tests.test_thread_isolation.test_rebuild_after_thread_migration_keeps_single_task|test_rebuild_after_thread_migration_keeps_single_task]]
- [[backend.tests.test_thread_isolation.test_task_fingerprint_dual_form_dedupe|test_task_fingerprint_dual_form_dedupe]]

## Side Effects

- none statically observed
