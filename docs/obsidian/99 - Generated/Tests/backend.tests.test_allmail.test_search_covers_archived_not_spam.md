---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_allmail
qualified_name: backend.tests.test_allmail.test_search_covers_archived_not_spam
source: backend/tests/test_allmail.py
line: 112
status: active
tags: [test, function, test]
---

# test_search_covers_archived_not_spam

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_search_covers_archived_not_spam` in `backend/tests/test_allmail.py`.

## Location

`backend/tests/test_allmail.py:112`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.search_emails|search_emails]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)

## Reads

- [[table_emails]]
- [[table_emails_fts]]

## Writes

- [[table_emails]]

## Side Effects

- SQLite
