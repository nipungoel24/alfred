---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_allmail
qualified_name: backend.tests.test_allmail.test_all_scope_excludes_spam_trash_draft_only
source: backend/tests/test_allmail.py
line: 56
status: active
tags: [test, function, test]
---

# test_all_scope_excludes_spam_trash_draft_only

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_all_scope_excludes_spam_trash_draft_only` in `backend/tests/test_allmail.py`.

## Location

`backend/tests/test_allmail.py:56`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.emails_filtered|emails_filtered]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)

## Reads

- [[table_emails]]

## Writes

- [[table_emails]]

## Side Effects

- SQLite
