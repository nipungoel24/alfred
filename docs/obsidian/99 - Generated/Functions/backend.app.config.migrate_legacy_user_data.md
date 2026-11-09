---
type: function
generated: true
language: python
layer: backend
module: backend.app.config
qualified_name: backend.app.config.migrate_legacy_user_data
source: backend/app/config.py
line: 61
status: active
tags: [backend, function]
---

# migrate_legacy_user_data

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Move a legacy mailbox out of the install directory, or do nothing.

## Location

`backend/app/config.py:61`

## Signature

```python
() -> Path | None
```

## Returns

`Path | None`

## Calls

- `getLogger` (`logging.getLogger`, calls-inferred)
- `getenv` (`os.getenv`, calls-inferred)
- `replace` (`os.replace`, calls-inferred)

## Called By

- [[backend.tests.test_legacy_data_migration.test_a_failed_move_keeps_the_mailbox_readable|test_a_failed_move_keeps_the_mailbox_readable]]
- [[backend.tests.test_legacy_data_migration.test_a_legacy_mailbox_moves_into_alfreddata|test_a_legacy_mailbox_moves_into_alfreddata]]
- [[backend.tests.test_legacy_data_migration.test_an_explicit_database_path_never_moves_user_data|test_an_explicit_database_path_never_moves_user_data]]
- [[backend.tests.test_legacy_data_migration.test_an_unclean_shutdown_defers_the_move|test_an_unclean_shutdown_defers_the_move]]
- [[backend.tests.test_legacy_data_migration.test_either_sidecar_alone_defers_the_move|test_either_sidecar_alone_defers_the_move]]
- [[backend.tests.test_legacy_data_migration.test_migration_is_not_attempted_twice|test_migration_is_not_attempted_twice]]
- [[backend.tests.test_legacy_data_migration.test_nothing_happens_when_there_is_no_legacy_mailbox|test_nothing_happens_when_there_is_no_legacy_mailbox]]
- [[backend.tests.test_legacy_data_migration.test_resolve_reports_the_new_location_once_migration_has_run|test_resolve_reports_the_new_location_once_migration_has_run]]
- [[backend.tests.test_legacy_data_migration.test_the_installed_binaries_are_left_where_they_are|test_the_installed_binaries_are_left_where_they_are]]
- [[backend.tests.test_legacy_data_migration.test_the_users_own_backups_travel_with_the_mailbox|test_the_users_own_backups_travel_with_the_mailbox]]
- [[backend.tests.test_legacy_data_migration.test_two_databases_are_left_alone|test_two_databases_are_left_alone]]

## Side Effects

- none statically observed
