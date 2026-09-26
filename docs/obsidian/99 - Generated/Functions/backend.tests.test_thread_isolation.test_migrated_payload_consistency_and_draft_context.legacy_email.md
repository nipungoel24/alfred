---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_thread_isolation.test_migrated_payload_consistency_and_draft_context
qualified_name: backend.tests.test_thread_isolation.test_migrated_payload_consistency_and_draft_context.legacy_email
source: backend/tests/test_thread_isolation.py
line: 295
status: active
tags: [test, function]
---

# legacy_email

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `legacy_email` in `backend/tests/test_thread_isolation.py`.

## Location

`backend/tests/test_thread_isolation.py:295`

## Signature

```python
(raw_id, account, subject, sender = 'a@example.com')
```

## Parameters

- `raw_id`
- `account`
- `subject`
- `sender`

## Calls

- [[backend.app.schemas.Email|Email]] (calls)

## Writes

- [[table_emails]]

## Side Effects

- SQLite
