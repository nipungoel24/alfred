---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_gmail_mock
qualified_name: backend.tests.test_gmail_mock.test_gmail_sync_incremental
source: backend/tests/test_gmail_mock.py
line: 130
status: active
tags: [test, function, test]
---

# test_gmail_sync_incremental

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_gmail_sync_incremental` in `backend/tests/test_gmail_mock.py`.

## Location

`backend/tests/test_gmail_mock.py:130`

## Signature

```python
(mock_get, mock_gmail, temp_repo)
```

## Parameters

- `mock_get`
- `mock_gmail`
- `temp_repo`

## Calls

- `run` (`asyncio.run`, calls-inferred)
- [[backend.app.schemas.Email|Email]] (calls)
- [[backend.app.schemas.EmailAccount|EmailAccount]] (calls)
- `now` (`datetime.datetime.now`, calls-inferred)
- `timedelta` (`datetime.timedelta`, calls-inferred)
- `dumps` (`json.dumps`, calls-inferred)
- `loads` (`json.loads`, calls-inferred)
- `MagicMock` (`unittest.mock.MagicMock`, calls-inferred)

## Reads

- [[table_emails]]

## Side Effects

- SQLite
