---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_eligibility
qualified_name: backend.tests.test_eligibility.test_history_label_changes_refresh_via_metadata
source: backend/tests/test_eligibility.py
line: 340
status: active
tags: [test, function, test]
---

# test_history_label_changes_refresh_via_metadata

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_history_label_changes_refresh_via_metadata` in `backend/tests/test_eligibility.py`.

## Location

`backend/tests/test_eligibility.py:340`

## Signature

```python
(mock_get, repo)
```

## Parameters

- `mock_get`
- `repo`

## Calls

- `run` (`asyncio.run`, calls-inferred)
- [[backend.app.db.repositories.Repository.email|email]] (calls)
- [[backend.app.db.repositories.Repository.email_eligibility|email_eligibility]] (calls)
- [[backend.app.db.repositories.Repository.save_account|save_account]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)
- `now` (`datetime.datetime.now`, calls-inferred)
- `timedelta` (`datetime.timedelta`, calls-inferred)
- `dumps` (`json.dumps`, calls-inferred)
- `MagicMock` (`unittest.mock.MagicMock`, calls-inferred)

## Reads

- [[table_emails]]

## Writes

- [[table_accounts]]
- [[table_emails]]

## Side Effects

- SQLite
