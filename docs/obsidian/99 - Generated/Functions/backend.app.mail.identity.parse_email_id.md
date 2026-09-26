---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.identity
qualified_name: backend.app.mail.identity.parse_email_id
source: backend/app/mail/identity.py
line: 49
status: active
tags: [gmail, function]
---

# parse_email_id

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Split a scoped local id into (account_id, provider_message_id).

## Location

`backend/app/mail/identity.py:49`

## Signature

```python
(email_id: str) -> tuple[str | None, str | None]
```

## Parameters

- `email_id` (`str`)

## Returns

`tuple[str | None, str | None]`

## Called By

- [[backend.tests.test_identity_migration.test_identity_double_prefix_never_scopes_twice|test_identity_double_prefix_never_scopes_twice]]
- [[backend.tests.test_identity_migration.test_identity_legacy_raw_id_not_scoped|test_identity_legacy_raw_id_not_scoped]]
- [[backend.tests.test_identity_migration.test_identity_round_trip|test_identity_round_trip]]
- [[backend.tests.test_identity_migration.test_identity_underscore_email|test_identity_underscore_email]]

## Side Effects

- none statically observed
