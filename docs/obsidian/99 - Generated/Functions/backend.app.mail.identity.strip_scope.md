---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.identity
qualified_name: backend.app.mail.identity.strip_scope
source: backend/app/mail/identity.py
line: 98
status: active
tags: [gmail, function]
---

# strip_scope

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Remove a known account prefix, returning the provider-side id.

## Location

`backend/app/mail/identity.py:98`

## Signature

```python
(scoped_id: str, account_id: str) -> str
```

## Parameters

- `scoped_id` (`str`)
- `account_id` (`str`)

## Returns

`str`

## Called By

- [[backend.app.main._label_backfill|_label_backfill]]
- [[backend.tests.test_thread_isolation.test_strip_scope_rejects_foreign_ids|test_strip_scope_rejects_foreign_ids]]

## Side Effects

- none statically observed
