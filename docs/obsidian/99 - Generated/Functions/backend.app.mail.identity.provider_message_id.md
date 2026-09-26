---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.identity
qualified_name: backend.app.mail.identity.provider_message_id
source: backend/app/mail/identity.py
line: 63
status: active
tags: [gmail, function]
---

# provider_message_id

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

The provider-side message id for a local id, or None if not scoped.

## Location

`backend/app/mail/identity.py:63`

## Signature

```python
(email_id: str) -> str | None
```

## Parameters

- `email_id` (`str`)

## Returns

`str | None`

## Called By

- [[backend.app.main._label_backfill|_label_backfill]]
- [[backend.tests.test_identity_migration.test_identity_round_trip|test_identity_round_trip]]
- [[backend.tests.test_multi_account.test_same_provider_message_id_collision|test_same_provider_message_id_collision]]

## Side Effects

- none statically observed
