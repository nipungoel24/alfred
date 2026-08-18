---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_allmail
qualified_name: backend.tests.test_allmail.test_counts_report_inbox_allmail_excluded
source: backend/tests/test_allmail.py
line: 121
status: active
tags: [test, function, test]
---

# test_counts_report_inbox_allmail_excluded

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_counts_report_inbox_allmail_excluded` in `backend/tests/test_allmail.py`.

## Location

`backend/tests/test_allmail.py:121`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.email_counts|email_counts]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)

## Reads

- [[table_emails]]

## Writes

- [[table_emails]]

## Side Effects

- SQLite
