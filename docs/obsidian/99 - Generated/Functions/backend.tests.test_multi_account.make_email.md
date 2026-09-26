---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_multi_account
qualified_name: backend.tests.test_multi_account.make_email
source: backend/tests/test_multi_account.py
line: 16
status: active
tags: [test, function]
---

# make_email

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `make_email` in `backend/tests/test_multi_account.py`.

## Location

`backend/tests/test_multi_account.py:16`

## Signature

```python
(id: str = 'e1', sender: str = 'alice@example.com', subject: str = 'Hello World', body: str = 'Test body', account_id: str | None = None) -> Email
```

## Parameters

- `id` (`str`)
- `sender` (`str`)
- `subject` (`str`)
- `body` (`str`)
- `account_id` (`str | None`)

## Returns

`Email`

## Calls

- [[backend.app.schemas.Email|Email]] (calls)

## Side Effects

- none statically observed
