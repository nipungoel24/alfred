---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_fts_upgrade
qualified_name: backend.tests.test_fts_upgrade.make_email
source: backend/tests/test_fts_upgrade.py
line: 35
status: active
tags: [test, function]
---

# make_email

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `make_email` in `backend/tests/test_fts_upgrade.py`.

## Location

`backend/tests/test_fts_upgrade.py:35`

## Signature

```python
(id: str = 'e1', subject: str = 'Hello World', body: str = 'Test body', account_id: str | None = None) -> Email
```

## Parameters

- `id` (`str`)
- `subject` (`str`)
- `body` (`str`)
- `account_id` (`str | None`)

## Returns

`Email`

## Calls

- [[backend.app.schemas.Email|Email]] (calls)

## Side Effects

- none statically observed
