---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_allmail
qualified_name: backend.tests.test_allmail.test_backfill_skips_cached_rows_and_updates_labels
source: backend/tests/test_allmail.py
line: 281
status: active
tags: [test, function, test]
---

# test_backfill_skips_cached_rows_and_updates_labels

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_backfill_skips_cached_rows_and_updates_labels` in `backend/tests/test_allmail.py`.

## Location

`backend/tests/test_allmail.py:281`

## Signature

```python
(mock_get, repo)
```

## Parameters

- `mock_get`
- `repo`

## Calls

- `run` (`asyncio.run`, calls-inferred)
- [[backend.app.db.repositories.Repository.email_counts|email_counts]] (calls)
- [[backend.app.db.repositories.Repository.email_eligibility|email_eligibility]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)
- [[backend.app.mail.providers.gmail.GmailProvider|GmailProvider]] (calls)
- `now` (`datetime.datetime.now`, calls-inferred)
- `timedelta` (`datetime.timedelta`, calls-inferred)
- `dumps` (`json.dumps`, calls-inferred)
- `MagicMock` (`unittest.mock.MagicMock`, calls-inferred)

## Reads

- [[table_emails]]

## Writes

- [[table_emails]]

## Side Effects

- SQLite
