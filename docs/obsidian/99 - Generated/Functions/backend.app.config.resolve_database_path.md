---
type: function
generated: true
language: python
layer: backend
module: backend.app.config
qualified_name: backend.app.config.resolve_database_path
source: backend/app/config.py
line: 140
status: active
tags: [backend, function]
---

# resolve_database_path

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

The database path to use. Reports; never moves anything.

## Location

`backend/app/config.py:140`

## Signature

```python
() -> Path
```

## Returns

`Path`

## Calls

- `getenv` (`os.getenv`, calls-inferred)
- `Path` (`pathlib.Path`, calls-inferred)

## Called By

- [[backend.tests.test_legacy_data_migration.test_a_blank_override_is_treated_as_absent|test_a_blank_override_is_treated_as_absent]]
- [[backend.tests.test_legacy_data_migration.test_a_failed_move_keeps_the_mailbox_readable|test_a_failed_move_keeps_the_mailbox_readable]]
- [[backend.tests.test_legacy_data_migration.test_a_fresh_install_resolves_to_alfreddata_without_creating_anything|test_a_fresh_install_resolves_to_alfreddata_without_creating_anything]]
- [[backend.tests.test_legacy_data_migration.test_an_explicit_database_path_never_moves_user_data|test_an_explicit_database_path_never_moves_user_data]]
- [[backend.tests.test_legacy_data_migration.test_resolve_reports_the_new_location_once_migration_has_run|test_resolve_reports_the_new_location_once_migration_has_run]]
- [[backend.tests.test_legacy_data_migration.test_resolving_the_path_never_moves_anything|test_resolving_the_path_never_moves_anything]]

## Side Effects

- none statically observed
