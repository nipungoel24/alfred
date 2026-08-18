---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.eligible_emails_without_analysis
source: backend/app/db/repositories.py
line: 289
status: active
tags: [database, function]
---

# eligible_emails_without_analysis

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

ACTIVE-Inbox messages that still need analysis (for the queue).

## Location

`backend/app/db/repositories.py:289`

## Signature

```python
(self, model: str, schema = '1', account_id: str | None = None) -> list[Email]
```

## Parameters

- `self`
- `model` (`str`)
- `schema`
- `account_id` (`str | None`)

## Returns

`list[Email]`

## Calls

- `model_validate_json` (`backend.app.schemas.Email.model_validate_json`, calls-inferred)

## Called By

- [[backend.tests.test_allmail.test_archived_excluded_from_intelligence|test_archived_excluded_from_intelligence]]
- [[backend.tests.test_allmail.test_sent_visible_but_excluded_from_intelligence|test_sent_visible_but_excluded_from_intelligence]]

## Reads

- [[table_email_analysis]]
- [[table_emails]]

## Side Effects

- SQLite
