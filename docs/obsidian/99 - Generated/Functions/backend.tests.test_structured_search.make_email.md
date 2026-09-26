---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_structured_search
qualified_name: backend.tests.test_structured_search.make_email
source: backend/tests/test_structured_search.py
line: 25
status: active
tags: [test, function]
---

# make_email

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `make_email` in `backend/tests/test_structured_search.py`.

## Location

`backend/tests/test_structured_search.py:25`

## Signature

```python
(id: str = 'e1', sender: str = 'alice@example.com', subject: str = 'Hello World', body: str = 'Test body', received_at: str = '2024-01-15T10:00:00') -> Email
```

## Parameters

- `id` (`str`)
- `sender` (`str`)
- `subject` (`str`)
- `body` (`str`)
- `received_at` (`str`)

## Returns

`Email`

## Calls

- [[backend.app.schemas.Email|Email]] (calls)

## Side Effects

- none statically observed
