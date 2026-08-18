---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.mark_email_excluded
source: backend/app/db/repositories.py
line: 160
status: active
tags: [database, function]
---

# mark_email_excluded

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Exclude a cached message from all current-attention projections.

## Location

`backend/app/db/repositories.py:160`

## Signature

```python
(self, email_id: str) -> bool
```

## Parameters

- `self`
- `email_id` (`str`)

## Returns

`bool`

## Called By

- [[backend.app.mail.providers.gmail.GmailProvider.sync_messages|sync_messages]]
- [[backend.tests.test_eligibility.test_permanent_delete_marks_excluded_not_destroyed|test_permanent_delete_marks_excluded_not_destroyed]]

## Writes

- [[table_emails]]

## Side Effects

- SQLite
