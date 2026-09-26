---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_identity_migration
source: backend/tests/test_identity_migration.py
status: active
tags: [module, backend]
---

# backend.tests.test_identity_migration

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_identity_migration.py`

## Imports

- `Category` ← `backend.app.schemas.Category`
- `Email` ← `backend.app.schemas.Email`
- `EmailAnalysis` ← `backend.app.schemas.EmailAnalysis`
- `FTS_SCHEMA` ← `backend.app.db.database.FTS_SCHEMA`
- `INDEXES` ← `backend.app.db.database.INDEXES`
- `Path` ← `pathlib.Path`
- `Priority` ← `backend.app.schemas.Priority`
- `Repository` ← `backend.app.db.repositories.Repository`
- `SCHEMA` ← `backend.app.db.database.SCHEMA`
- `connect` ← `backend.app.db.database.connect`
- `is_scoped_for` ← `backend.app.mail.identity.is_scoped_for`
- `json` ← `json`
- `parse_email_id` ← `backend.app.mail.identity.parse_email_id`
- `provider_message_id` ← `backend.app.mail.identity.provider_message_id`
- `pytest` ← `pytest`
- `scoped_email_id` ← `backend.app.mail.identity.scoped_email_id`
- `sqlite3` ← `sqlite3`

## Functions

- [[backend.tests.test_identity_migration._legacy_payload|_legacy_payload]]

## Tests

- [[backend.tests.test_identity_migration.test_backup_failure_aborts_migration|test_backup_failure_aborts_migration]]
- [[backend.tests.test_identity_migration.test_backup_is_readable_snapshot|test_backup_is_readable_snapshot]]
- [[backend.tests.test_identity_migration.test_identity_double_prefix_never_scopes_twice|test_identity_double_prefix_never_scopes_twice]]
- [[backend.tests.test_identity_migration.test_identity_legacy_raw_id_not_scoped|test_identity_legacy_raw_id_not_scoped]]
- [[backend.tests.test_identity_migration.test_identity_round_trip|test_identity_round_trip]]
- [[backend.tests.test_identity_migration.test_identity_underscore_email|test_identity_underscore_email]]
- [[backend.tests.test_identity_migration.test_migration_is_idempotent|test_migration_is_idempotent]]
- [[backend.tests.test_identity_migration.test_migration_rekeys_legacy_database|test_migration_rekeys_legacy_database]]
- [[backend.tests.test_identity_migration.test_non_hex_scoped_identities_never_double_prefix|test_non_hex_scoped_identities_never_double_prefix]]
- [[backend.tests.test_identity_migration.test_null_provider_rows_exempt_from_uniqueness|test_null_provider_rows_exempt_from_uniqueness]]
- [[backend.tests.test_identity_migration.test_provider_uniqueness_enforced|test_provider_uniqueness_enforced]]
