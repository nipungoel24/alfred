---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_task_reconcile_idempotency
qualified_name: backend.tests.test_task_reconcile_idempotency.make_email
source: backend/tests/test_task_reconcile_idempotency.py
line: 60
status: active
tags: [test, function]
---

# make_email

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `make_email` in `backend/tests/test_task_reconcile_idempotency.py`.

## Location

`backend/tests/test_task_reconcile_idempotency.py:60`

## Signature

```python
(email_id: str, thread_id: str, subject = 'Test', labels = None) -> Email
```

## Parameters

- `email_id` (`str`)
- `thread_id` (`str`)
- `subject`
- `labels`

## Returns

`Email`

## Calls

- [[backend.app.schemas.Email|Email]] (calls)

## Side Effects

- none statically observed
