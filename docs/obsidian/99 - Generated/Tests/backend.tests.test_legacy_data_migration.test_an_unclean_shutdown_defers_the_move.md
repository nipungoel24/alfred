---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_legacy_data_migration
qualified_name: backend.tests.test_legacy_data_migration.test_an_unclean_shutdown_defers_the_move
source: backend/tests/test_legacy_data_migration.py
line: 87
status: active
tags: [test, function, test]
---

# test_an_unclean_shutdown_defers_the_move

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

A `-wal` beside the database means unrecovered transactions.

## Location

`backend/tests/test_legacy_data_migration.py:87`

## Signature

```python
(local_app_data, caplog)
```

## Parameters

- `local_app_data`
- `caplog`

## Calls

- [[backend.app.config.migrate_legacy_user_data|migrate_legacy_user_data]] (calls)

## Side Effects

- none statically observed
