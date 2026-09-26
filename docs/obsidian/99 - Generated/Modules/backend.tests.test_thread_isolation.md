---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_thread_isolation
source: backend/tests/test_thread_isolation.py
status: active
tags: [module, backend]
---

# backend.tests.test_thread_isolation

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_thread_isolation.py`

## Imports

- `Email` ← `backend.app.schemas.Email`
- `GmailProvider` ← `backend.app.mail.providers.gmail.GmailProvider`
- `Path` ← `pathlib.Path`
- `Repository` ← `backend.app.db.repositories.Repository`
- `TestClient` ← `fastapi.testclient.TestClient`
- `_normalize_action` ← `backend.app.services.task_derivation._normalize_action`
- `base64` ← `base64`
- `candidate_fingerprints` ← `backend.app.services.task_derivation.candidate_fingerprints`
- `parse_thread_id` ← `backend.app.mail.identity.parse_thread_id`
- `pytest` ← `pytest`
- `scoped_email_id` ← `backend.app.mail.identity.scoped_email_id`
- `scoped_thread_id` ← `backend.app.mail.identity.scoped_thread_id`
- `strip_scope` ← `backend.app.mail.identity.strip_scope`
- `task_fingerprint` ← `backend.app.services.task_derivation.task_fingerprint`

## Functions

- [[backend.tests.test_thread_isolation.gmail_detail|gmail_detail]]
- [[backend.tests.test_thread_isolation.isolated_app|isolated_app]]
- [[backend.tests.test_thread_isolation.provider|provider]]
- [[backend.tests.test_thread_isolation.test_draft_endpoint_isolation.fake_draft|fake_draft]]
- [[backend.tests.test_thread_isolation.test_migrated_payload_consistency_and_draft_context.legacy_email|legacy_email]]

## Tests

- [[backend.tests.test_thread_isolation.test_draft_endpoint_isolation|test_draft_endpoint_isolation]]
- [[backend.tests.test_thread_isolation.test_migrated_payload_consistency_and_draft_context|test_migrated_payload_consistency_and_draft_context]]
- [[backend.tests.test_thread_isolation.test_rebuild_after_thread_migration_keeps_single_task|test_rebuild_after_thread_migration_keeps_single_task]]
- [[backend.tests.test_thread_isolation.test_scoped_thread_identity|test_scoped_thread_identity]]
- [[backend.tests.test_thread_isolation.test_strip_scope_rejects_foreign_ids|test_strip_scope_rejects_foreign_ids]]
- [[backend.tests.test_thread_isolation.test_task_fingerprint_dual_form_dedupe|test_task_fingerprint_dual_form_dedupe]]
- [[backend.tests.test_thread_isolation.test_thread_migration_rekeys_legacy_rows|test_thread_migration_rekeys_legacy_rows]]
- [[backend.tests.test_thread_isolation.test_thread_query_isolation|test_thread_query_isolation]]

## Constants

- `PROVIDER_THREAD`
- `RAW_A`
- `RAW_B`
