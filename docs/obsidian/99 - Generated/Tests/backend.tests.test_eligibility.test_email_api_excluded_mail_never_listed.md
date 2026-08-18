---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_eligibility
qualified_name: backend.tests.test_eligibility.test_email_api_excluded_mail_never_listed
source: backend/tests/test_eligibility.py
line: 425
status: active
tags: [test, function, test]
---

# test_email_api_excluded_mail_never_listed

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Spam/trash/archived produce zero briefing candidates and zero

## Location

`backend/tests/test_eligibility.py:425`

## Signature

```python
(repo, tmp_path)
```

## Parameters

- `repo`
- `tmp_path`

## Calls

- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)

## Writes

- [[table_emails]]

## Side Effects

- SQLite
