---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.emails_by_thread
source: backend/app/db/repositories.py
line: 346
status: active
tags: [database, function]
---

# emails_by_thread

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Fetch emails in a thread, ordered chronologically.

## Location

`backend/app/db/repositories.py:346`

## Signature

```python
(self, thread_id: str) -> list[Email]
```

## Parameters

- `self`
- `thread_id` (`str`)

## Returns

`list[Email]`

## Calls

- `model_validate_json` (`backend.app.schemas.Email.model_validate_json`, calls-inferred)

## Called By

- [[backend.tests.test_eligibility.test_mixed_label_thread_keeps_active_messages_visible|test_mixed_label_thread_keeps_active_messages_visible]]

## Reads

- [[table_emails]]

## Side Effects

- SQLite
