---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.identity
qualified_name: backend.app.mail.identity.is_scoped_for
source: backend/app/mail/identity.py
line: 68
status: active
tags: [gmail, function]
---

# is_scoped_for

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

True when the local id was generated for the given account.

## Location

`backend/app/mail/identity.py:68`

## Signature

```python
(email_id: str, account_id: str) -> bool
```

## Parameters

- `email_id` (`str`)
- `account_id` (`str`)

## Returns

`bool`

## Called By

- [[backend.tests.test_identity_migration.test_identity_underscore_email|test_identity_underscore_email]]
- [[backend.tests.test_identity_migration.test_non_hex_scoped_identities_never_double_prefix|test_non_hex_scoped_identities_never_double_prefix]]

## Side Effects

- none statically observed
