---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_legacy_data_migration
source: backend/tests/test_legacy_data_migration.py
status: active
tags: [module, backend]
---

# backend.tests.test_legacy_data_migration

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_legacy_data_migration.py`

## Imports

- `Path` ← `pathlib.Path`
- `config` ← `backend.app.config`
- `logging` ← `logging`
- `pytest` ← `pytest`

## Functions

- [[backend.tests.test_legacy_data_migration._make_legacy|_make_legacy]]
- [[backend.tests.test_legacy_data_migration.local_app_data|local_app_data]]
- [[backend.tests.test_legacy_data_migration.test_a_failed_move_keeps_the_mailbox_readable.refuse|refuse]]

## Tests

- [[backend.tests.test_legacy_data_migration.test_a_blank_override_is_treated_as_absent|test_a_blank_override_is_treated_as_absent]]
- [[backend.tests.test_legacy_data_migration.test_a_failed_move_keeps_the_mailbox_readable|test_a_failed_move_keeps_the_mailbox_readable]]
- [[backend.tests.test_legacy_data_migration.test_a_fresh_install_resolves_to_alfreddata_without_creating_anything|test_a_fresh_install_resolves_to_alfreddata_without_creating_anything]]
- [[backend.tests.test_legacy_data_migration.test_a_legacy_mailbox_moves_into_alfreddata|test_a_legacy_mailbox_moves_into_alfreddata]]
- [[backend.tests.test_legacy_data_migration.test_an_explicit_database_path_never_moves_user_data|test_an_explicit_database_path_never_moves_user_data]]
- [[backend.tests.test_legacy_data_migration.test_an_unclean_shutdown_defers_the_move|test_an_unclean_shutdown_defers_the_move]]
- [[backend.tests.test_legacy_data_migration.test_either_sidecar_alone_defers_the_move|test_either_sidecar_alone_defers_the_move]]
- [[backend.tests.test_legacy_data_migration.test_migration_is_not_attempted_twice|test_migration_is_not_attempted_twice]]
- [[backend.tests.test_legacy_data_migration.test_nothing_happens_when_there_is_no_legacy_mailbox|test_nothing_happens_when_there_is_no_legacy_mailbox]]
- [[backend.tests.test_legacy_data_migration.test_resolve_reports_the_new_location_once_migration_has_run|test_resolve_reports_the_new_location_once_migration_has_run]]
- [[backend.tests.test_legacy_data_migration.test_resolving_the_path_never_moves_anything|test_resolving_the_path_never_moves_anything]]
- [[backend.tests.test_legacy_data_migration.test_the_installed_binaries_are_left_where_they_are|test_the_installed_binaries_are_left_where_they_are]]
- [[backend.tests.test_legacy_data_migration.test_the_legacy_path_is_still_reported_while_it_is_in_use|test_the_legacy_path_is_still_reported_while_it_is_in_use]]
- [[backend.tests.test_legacy_data_migration.test_the_users_own_backups_travel_with_the_mailbox|test_the_users_own_backups_travel_with_the_mailbox]]
- [[backend.tests.test_legacy_data_migration.test_two_databases_are_left_alone|test_two_databases_are_left_alone]]

## Constants

- `LEGACY_BYTES`
