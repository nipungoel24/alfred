---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_legacy_data_migration
qualified_name: backend.tests.test_legacy_data_migration.test_a_failed_move_keeps_the_mailbox_readable
source: backend/tests/test_legacy_data_migration.py
line: 125
status: active
tags: [test, function, test]
---

# test_a_failed_move_keeps_the_mailbox_readable

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

If the rename fails the app must still find its data.

## Location

`backend/tests/test_legacy_data_migration.py:125`

## Signature

```python
(local_app_data, monkeypatch, caplog)
```

## Parameters

- `local_app_data`
- `monkeypatch`
- `caplog`

## Calls

- [[backend.app.config.migrate_legacy_user_data|migrate_legacy_user_data]] (calls)
- [[backend.app.config.resolve_database_path|resolve_database_path]] (calls)

## Side Effects

- none statically observed
