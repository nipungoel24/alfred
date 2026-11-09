---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_legacy_data_migration
qualified_name: backend.tests.test_legacy_data_migration.test_resolve_reports_the_new_location_once_migration_has_run
source: backend/tests/test_legacy_data_migration.py
line: 152
status: active
tags: [test, function, test]
---

# test_resolve_reports_the_new_location_once_migration_has_run

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

`resolve_database_path` does not migrate; it reports.

## Location

`backend/tests/test_legacy_data_migration.py:152`

## Signature

```python
(local_app_data)
```

## Parameters

- `local_app_data`

## Calls

- [[backend.app.config.migrate_legacy_user_data|migrate_legacy_user_data]] (calls)
- [[backend.app.config.resolve_database_path|resolve_database_path]] (calls)

## Side Effects

- none statically observed
