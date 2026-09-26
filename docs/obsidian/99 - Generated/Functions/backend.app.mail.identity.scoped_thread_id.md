---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.identity
qualified_name: backend.app.mail.identity.scoped_thread_id
source: backend/app/mail/identity.py
line: 84
status: active
tags: [gmail, function]
---

# scoped_thread_id

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Build the local scoped identity for a provider thread.

## Location

`backend/app/mail/identity.py:84`

## Signature

```python
(account_id: str, provider_thread_id: str | None) -> str | None
```

## Parameters

- `account_id` (`str`)
- `provider_thread_id` (`str | None`)

## Returns

`str | None`

## Called By

- [[backend.app.mail.providers.gmail.GmailProvider._normalize_message|_normalize_message]]
- [[backend.tests.test_thread_isolation.test_migrated_payload_consistency_and_draft_context|test_migrated_payload_consistency_and_draft_context]]
- [[backend.tests.test_thread_isolation.test_rebuild_after_thread_migration_keeps_single_task|test_rebuild_after_thread_migration_keeps_single_task]]
- [[backend.tests.test_thread_isolation.test_scoped_thread_identity|test_scoped_thread_identity]]
- [[backend.tests.test_thread_isolation.test_task_fingerprint_dual_form_dedupe|test_task_fingerprint_dual_form_dedupe]]
- [[backend.tests.test_thread_isolation.test_thread_migration_rekeys_legacy_rows|test_thread_migration_rekeys_legacy_rows]]

## Side Effects

- none statically observed
