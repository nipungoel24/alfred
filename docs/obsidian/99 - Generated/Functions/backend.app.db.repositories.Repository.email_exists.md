---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.email_exists
source: backend/app/db/repositories.py
line: 97
status: active
tags: [database, function]
---

# email_exists

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Check if email exists without deserializing payload.

## Location

`backend/app/db/repositories.py:97`

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

- [[backend.app.mail.providers.gmail.GmailProvider.backfill_messages|backfill_messages]]
- [[backend.app.mail.providers.gmail.GmailProvider.sync_messages|sync_messages]]
- [[backend.tests.test_eligibility.test_spam_transition_hides_from_projections|test_spam_transition_hides_from_projections]]

## Reads

- [[table_emails]]

## Side Effects

- SQLite
