---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.identity
qualified_name: backend.app.mail.identity.scoped_email_id
source: backend/app/mail/identity.py
line: 42
status: active
tags: [gmail, function]
---

# scoped_email_id

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Build the local scoped identity for a provider message.

## Location

`backend/app/mail/identity.py:42`

## Signature

```python
(account_id: str, provider_message_id: str) -> str
```

## Parameters

- `account_id` (`str`)
- `provider_message_id` (`str`)

## Returns

`str`

## Called By

- [[backend.app.mail.providers.gmail.GmailProvider._normalize_message|_normalize_message]]
- [[backend.app.mail.providers.gmail.GmailProvider.backfill_messages|backfill_messages]]
- [[backend.app.mail.providers.gmail.GmailProvider.sync_messages|sync_messages]]
- [[backend.tests.test_identity_migration.test_backup_failure_aborts_migration|test_backup_failure_aborts_migration]]
- [[backend.tests.test_identity_migration.test_identity_double_prefix_never_scopes_twice|test_identity_double_prefix_never_scopes_twice]]
- [[backend.tests.test_identity_migration.test_identity_round_trip|test_identity_round_trip]]
- [[backend.tests.test_identity_migration.test_identity_underscore_email|test_identity_underscore_email]]
- [[backend.tests.test_identity_migration.test_migration_is_idempotent|test_migration_is_idempotent]]
- [[backend.tests.test_identity_migration.test_migration_rekeys_legacy_database|test_migration_rekeys_legacy_database]]
- [[backend.tests.test_identity_migration.test_provider_uniqueness_enforced|test_provider_uniqueness_enforced]]
- [[backend.tests.test_multi_account.test_same_provider_message_id_collision|test_same_provider_message_id_collision]]
- [[backend.tests.test_thread_isolation.test_migrated_payload_consistency_and_draft_context|test_migrated_payload_consistency_and_draft_context]]
- [[backend.tests.test_thread_isolation.test_rebuild_after_thread_migration_keeps_single_task|test_rebuild_after_thread_migration_keeps_single_task]]

## Side Effects

- none statically observed
