---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_legacy_data_migration
qualified_name: backend.tests.test_legacy_data_migration.test_an_explicit_database_path_never_moves_user_data
source: backend/tests/test_legacy_data_migration.py
line: 187
status: active
tags: [test, function, test]
---

# test_an_explicit_database_path_never_moves_user_data

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

A scratch or test run must leave the real mailbox untouched.

## Location

`backend/tests/test_legacy_data_migration.py:187`

## Signature

```python
(local_app_data, monkeypatch)
```

## Parameters

- `local_app_data`
- `monkeypatch`

## Calls

- [[backend.app.config.migrate_legacy_user_data|migrate_legacy_user_data]] (calls)
- [[backend.app.config.resolve_database_path|resolve_database_path]] (calls)

## Side Effects

- none statically observed
