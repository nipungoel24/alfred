---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.search_emails
source: backend/app/db/repositories.py
line: 319
status: active
tags: [database, function]
---

# search_emails

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Full-text search using FTS5 if available, falling back to LIKE.

## Location

`backend/app/db/repositories.py:319`

## Signature

```python
(self, query: str, limit = 100) -> list[Email]
```

## Parameters

- `self`
- `query` (`str`)
- `limit`

## Returns

`list[Email]`

## Calls

- `model_validate_json` (`backend.app.schemas.Email.model_validate_json`, calls-inferred)

## Called By

- [[backend.tests.test_allmail.test_draft_excluded_from_all_mail_and_search|test_draft_excluded_from_all_mail_and_search]]
- [[backend.tests.test_allmail.test_search_covers_archived_not_spam|test_search_covers_archived_not_spam]]

## Reads

- [[table_emails]]
- [[table_emails_fts]]

## Side Effects

- SQLite
