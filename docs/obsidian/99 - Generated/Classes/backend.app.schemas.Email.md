---
type: class
generated: true
language: python
layer: backend
module: backend.app.schemas
qualified_name: backend.app.schemas.Email
source: backend/app/schemas.py
line: 24
status: active
tags: [backend, class]
---

# Email

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `Email` in `backend/app/schemas.py`.

## Location

`backend/app/schemas.py:24`

## Bases

- `BaseModel`

## Called By

- [[backend.app.mail.normalizer.normalized_email|normalized_email]]
- [[backend.app.mail.providers.gmail.GmailProvider._normalize_message|_normalize_message]]
- [[backend.tests.test_allmail._email|_email]]
- [[backend.tests.test_core.email|email]]
- [[backend.tests.test_eligibility._email|_email]]
- [[backend.tests.test_eligibility.test_search_within_category_context|test_search_within_category_context]]
- [[backend.tests.test_extended.get_email|get_email]]
- [[backend.tests.test_extended.test_prompt_injection_safety|test_prompt_injection_safety]]
- [[backend.tests.test_fts5.make_email|make_email]]
- [[backend.tests.test_fts_upgrade.make_email|make_email]]
- [[backend.tests.test_gmail_mock.test_gmail_sync_incremental|test_gmail_sync_incremental]]
- [[backend.tests.test_identity_migration._legacy_payload|_legacy_payload]]
- [[backend.tests.test_identity_migration.test_backup_failure_aborts_migration|test_backup_failure_aborts_migration]]
- [[backend.tests.test_identity_migration.test_backup_is_readable_snapshot|test_backup_is_readable_snapshot]]
- [[backend.tests.test_identity_migration.test_migration_is_idempotent|test_migration_is_idempotent]]
- [[backend.tests.test_identity_migration.test_non_hex_scoped_identities_never_double_prefix|test_non_hex_scoped_identities_never_double_prefix]]
- [[backend.tests.test_identity_migration.test_null_provider_rows_exempt_from_uniqueness|test_null_provider_rows_exempt_from_uniqueness]]
- [[backend.tests.test_identity_migration.test_provider_uniqueness_enforced|test_provider_uniqueness_enforced]]
- [[backend.tests.test_multi_account.make_email|make_email]]
- [[backend.tests.test_ollama_mock.test_ai_service_analyze_email_success|test_ai_service_analyze_email_success]]
- [[backend.tests.test_structured_search.make_email|make_email]]
- [[backend.tests.test_task_derivation.test_derive_tasks_adds_explicit_deadlines|test_derive_tasks_adds_explicit_deadlines]]
- [[backend.tests.test_task_derivation.test_derive_tasks_deduplicates_by_fingerprint|test_derive_tasks_deduplicates_by_fingerprint]]
- [[backend.tests.test_task_derivation.test_derive_tasks_ignores_newsletters_unless_urgent|test_derive_tasks_ignores_newsletters_unless_urgent]]
- [[backend.tests.test_task_derivation.test_derive_tasks_ignores_noise|test_derive_tasks_ignores_noise]]
- [[backend.tests.test_task_derivation.test_derive_tasks_ignores_third_party_owner|test_derive_tasks_ignores_third_party_owner]]
- [[backend.tests.test_task_migration.test_migration_idempotency_and_preservation|test_migration_idempotency_and_preservation]]
- [[backend.tests.test_task_migration.test_migration_rollback|test_migration_rollback]]
- [[backend.tests.test_task_user_corrections._seed_derived|_seed_derived]]
- [[backend.tests.test_task_user_corrections.test_migration_service_never_revives_dismissed|test_migration_service_never_revives_dismissed]]
- [[backend.tests.test_task_user_corrections.test_migration_service_respects_override|test_migration_service_respects_override]]
- [[backend.tests.test_thread_isolation.test_migrated_payload_consistency_and_draft_context|test_migrated_payload_consistency_and_draft_context]]
- [[backend.tests.test_thread_isolation.test_migrated_payload_consistency_and_draft_context.legacy_email|legacy_email]]
- [[backend.tests.test_thread_isolation.test_rebuild_after_thread_migration_keeps_single_task|test_rebuild_after_thread_migration_keeps_single_task]]
- [[backend.tests.test_thread_isolation.test_thread_migration_rekeys_legacy_rows|test_thread_migration_rekeys_legacy_rows]]

## Side Effects

- none statically observed
