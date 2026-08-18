---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_allmail
qualified_name: backend.tests.test_allmail.test_backfill_first_page_and_resume
source: backend/tests/test_allmail.py
line: 216
status: active
tags: [test, function, test]
---

# test_backfill_first_page_and_resume

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_backfill_first_page_and_resume` in `backend/tests/test_allmail.py`.

## Location

`backend/tests/test_allmail.py:216`

## Signature

```python
(mock_get, repo)
```

## Parameters

- `mock_get`
- `repo`

## Calls

- `run` (`asyncio.run`, calls-inferred)
- [[backend.app.db.repositories.Repository.account|account]] (calls)
- [[backend.app.db.repositories.Repository.email|email]] (calls)
- [[backend.app.db.repositories.Repository.email_counts|email_counts]] (calls)
- [[backend.app.mail.providers.gmail.GmailProvider|GmailProvider]] (calls)
- `now` (`datetime.datetime.now`, calls-inferred)
- `timedelta` (`datetime.timedelta`, calls-inferred)
- `loads` (`json.loads`, calls-inferred)
- `MagicMock` (`unittest.mock.MagicMock`, calls-inferred)

## Reads

- [[table_accounts]]
- [[table_emails]]

## Side Effects

- SQLite
