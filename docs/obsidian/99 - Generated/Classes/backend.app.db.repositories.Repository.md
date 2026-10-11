---
type: class
generated: true
language: python
layer: database
module: backend.app.db.repositories
qualified_name: backend.app.db.repositories.Repository
source: backend/app/db/repositories.py
line: 26
status: active
tags: [database, class]
---

# Repository

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `Repository` in `backend/app/db/repositories.py`.

## Location

`backend/app/db/repositories.py:26`

## Called By

- [[backend.tests.test_allmail.repo|repo]]
- [[backend.tests.test_backfill_jobs.repo|repo]]
- [[backend.tests.test_core.test_analysis_cache_invalidates_content_and_model|test_analysis_cache_invalidates_content_and_model]]
- [[backend.tests.test_core.test_briefing_cache_invalidates_when_analysis_changes|test_briefing_cache_invalidates_when_analysis_changes]]
- [[backend.tests.test_eligibility.repo|repo]]
- [[backend.tests.test_extended.test_api_endpoint_flows|test_api_endpoint_flows]]
- [[backend.tests.test_extended.test_cache_hit_and_invalidation|test_cache_hit_and_invalidation]]
- [[backend.tests.test_extended.test_persistence_restart|test_persistence_restart]]
- [[backend.tests.test_fts5.test_fts_body_truncation|test_fts_body_truncation]]
- [[backend.tests.test_fts5.test_fts_case_insensitive|test_fts_case_insensitive]]
- [[backend.tests.test_fts5.test_fts_delete_cleans_index|test_fts_delete_cleans_index]]
- [[backend.tests.test_fts5.test_fts_empty_body|test_fts_empty_body]]
- [[backend.tests.test_fts5.test_fts_fallback_to_like|test_fts_fallback_to_like]]
- [[backend.tests.test_fts5.test_fts_insert_and_search|test_fts_insert_and_search]]
- [[backend.tests.test_fts5.test_fts_insert_new_does_not_duplicate|test_fts_insert_new_does_not_duplicate]]
- [[backend.tests.test_fts5.test_fts_multiple_delete|test_fts_multiple_delete]]
- [[backend.tests.test_fts5.test_fts_multiple_emails|test_fts_multiple_emails]]
- [[backend.tests.test_fts5.test_fts_rebuild_removes_orphans|test_fts_rebuild_removes_orphans]]
- [[backend.tests.test_fts5.test_fts_search_no_match|test_fts_search_no_match]]
- [[backend.tests.test_fts5.test_fts_special_characters|test_fts_special_characters]]
- [[backend.tests.test_fts5.test_fts_update_without_manual_repair|test_fts_update_without_manual_repair]]
- [[backend.tests.test_fts5.test_fts_upsert_idempotent|test_fts_upsert_idempotent]]
- [[backend.tests.test_fts_upgrade.test_capability_probe_is_isolated|test_capability_probe_is_isolated]]
- [[backend.tests.test_fts_upgrade.test_existing_schema_detection|test_existing_schema_detection]]
- [[backend.tests.test_fts_upgrade.test_legacy_fts_schema_upgrades_through_connect|test_legacy_fts_schema_upgrades_through_connect]]
- [[backend.tests.test_fts_upgrade.test_old_sqlite_fallback_path|test_old_sqlite_fallback_path]]
- [[backend.tests.test_fts_upgrade.test_special_characters_search_literally|test_special_characters_search_literally]]
- [[backend.tests.test_gmail_mock.temp_repo|temp_repo]]
- [[backend.tests.test_identity_migration.test_backup_failure_aborts_migration|test_backup_failure_aborts_migration]]
- [[backend.tests.test_identity_migration.test_backup_is_readable_snapshot|test_backup_is_readable_snapshot]]
- [[backend.tests.test_identity_migration.test_migration_is_idempotent|test_migration_is_idempotent]]
- [[backend.tests.test_identity_migration.test_migration_rekeys_legacy_database|test_migration_rekeys_legacy_database]]
- [[backend.tests.test_identity_migration.test_non_hex_scoped_identities_never_double_prefix|test_non_hex_scoped_identities_never_double_prefix]]
- [[backend.tests.test_identity_migration.test_null_provider_rows_exempt_from_uniqueness|test_null_provider_rows_exempt_from_uniqueness]]
- [[backend.tests.test_identity_migration.test_provider_uniqueness_enforced|test_provider_uniqueness_enforced]]
- [[backend.tests.test_model_endpoints.client|client]]
- [[backend.tests.test_multi_account.test_account_credentials_isolation|test_account_credentials_isolation]]
- [[backend.tests.test_multi_account.test_account_id_stored_correctly|test_account_id_stored_correctly]]
- [[backend.tests.test_multi_account.test_account_prefixed_email_ids|test_account_prefixed_email_ids]]
- [[backend.tests.test_multi_account.test_account_specific_counts|test_account_specific_counts]]
- [[backend.tests.test_multi_account.test_delete_email_by_account|test_delete_email_by_account]]
- [[backend.tests.test_multi_account.test_emails_missing_labels_by_account|test_emails_missing_labels_by_account]]
- [[backend.tests.test_multi_account.test_label_update_by_account|test_label_update_by_account]]
- [[backend.tests.test_multi_account.test_same_provider_message_id_collision|test_same_provider_message_id_collision]]
- [[backend.tests.test_multi_account.test_search_respects_account_isolation|test_search_respects_account_isolation]]
- [[backend.tests.test_structured_search.test_account_scoped_structured_search|test_account_scoped_structured_search]]
- [[backend.tests.test_structured_search.test_filter_before_limit|test_filter_before_limit]]
- [[backend.tests.test_structured_search.test_structured_search_by_date|test_structured_search_by_date]]
- [[backend.tests.test_structured_search.test_structured_search_by_sender|test_structured_search_by_sender]]
- [[backend.tests.test_structured_search.test_structured_search_by_subject|test_structured_search_by_subject]]
- [[backend.tests.test_structured_search.test_structured_search_combined_filters|test_structured_search_combined_filters]]
- [[backend.tests.test_structured_search.test_structured_search_limit|test_structured_search_limit]]
- [[backend.tests.test_structured_search.test_structured_search_no_results|test_structured_search_no_results]]
- [[backend.tests.test_structured_search.test_structured_search_with_free_text|test_structured_search_with_free_text]]
- [[backend.tests.test_task_migration.repo|repo]]
- [[backend.tests.test_task_reconcile_idempotency.repo|repo]]
- [[backend.tests.test_task_reconcile_idempotency.test_reconcile_on_a_copy_of_the_live_database_is_idempotent|test_reconcile_on_a_copy_of_the_live_database_is_idempotent]]
- [[backend.tests.test_task_user_corrections.test_dismissal_survives_reopen|test_dismissal_survives_reopen]]
- [[backend.tests.test_task_user_corrections.test_migration_service_never_revives_dismissed|test_migration_service_never_revives_dismissed]]
- [[backend.tests.test_task_user_corrections.test_migration_service_respects_override|test_migration_service_respects_override]]
- [[backend.tests.test_thread_isolation.test_rebuild_after_thread_migration_keeps_single_task|test_rebuild_after_thread_migration_keeps_single_task]]
- [[backend.tests.test_thread_isolation.test_thread_migration_rekeys_legacy_rows|test_thread_migration_rekeys_legacy_rows]]
- [[backend.tests.test_thread_isolation.test_thread_query_isolation|test_thread_query_isolation]]

## Side Effects

- none statically observed
