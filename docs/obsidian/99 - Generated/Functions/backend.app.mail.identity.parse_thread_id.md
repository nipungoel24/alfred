---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.identity
qualified_name: backend.app.mail.identity.parse_thread_id
source: backend/app/mail/identity.py
line: 93
status: active
tags: [gmail, function]
---

# parse_thread_id

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Split a scoped local thread id into (account_id, provider_thread_id).

## Location

`backend/app/mail/identity.py:93`

## Signature

```python
(thread_id: str | None) -> tuple[str | None, str | None]
```

## Parameters

- `thread_id` (`str | None`)

## Returns

`tuple[str | None, str | None]`

## Called By

- [[backend.tests.test_thread_isolation.test_scoped_thread_identity|test_scoped_thread_identity]]

## Side Effects

- none statically observed
