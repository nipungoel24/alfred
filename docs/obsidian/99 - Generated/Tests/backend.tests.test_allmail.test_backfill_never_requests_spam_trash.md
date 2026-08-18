---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_allmail
qualified_name: backend.tests.test_allmail.test_backfill_never_requests_spam_trash
source: backend/tests/test_allmail.py
line: 303
status: active
tags: [test, function, test]
---

# test_backfill_never_requests_spam_trash

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_backfill_never_requests_spam_trash` in `backend/tests/test_allmail.py`.

## Location

`backend/tests/test_allmail.py:303`

## Signature

```python
(mock_get, repo)
```

## Parameters

- `mock_get`
- `repo`

## Calls

- `run` (`asyncio.run`, calls-inferred)
- [[backend.app.mail.providers.gmail.GmailProvider|GmailProvider]] (calls)
- `now` (`datetime.datetime.now`, calls-inferred)
- `timedelta` (`datetime.timedelta`, calls-inferred)
- `MagicMock` (`unittest.mock.MagicMock`, calls-inferred)

## Side Effects

- none statically observed
