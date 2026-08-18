---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_eligibility
qualified_name: backend.tests.test_eligibility.test_history_spam_arrival_is_never_cached
source: backend/tests/test_eligibility.py
line: 389
status: active
tags: [test, function, test]
---

# test_history_spam_arrival_is_never_cached

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_history_spam_arrival_is_never_cached` in `backend/tests/test_eligibility.py`.

## Location

`backend/tests/test_eligibility.py:389`

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
- [[backend.app.db.repositories.Repository.save_account|save_account]] (calls)
- `now` (`datetime.datetime.now`, calls-inferred)
- `timedelta` (`datetime.timedelta`, calls-inferred)
- `dumps` (`json.dumps`, calls-inferred)
- `MagicMock` (`unittest.mock.MagicMock`, calls-inferred)

## Reads

- [[table_emails]]

## Writes

- [[table_accounts]]

## Side Effects

- SQLite
