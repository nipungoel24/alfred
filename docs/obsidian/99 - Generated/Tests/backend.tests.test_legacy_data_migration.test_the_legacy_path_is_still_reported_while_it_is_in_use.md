---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_legacy_data_migration
qualified_name: backend.tests.test_legacy_data_migration.test_the_legacy_path_is_still_reported_while_it_is_in_use
source: backend/tests/test_legacy_data_migration.py
line: 213
status: active
tags: [test, function, test]
---

# test_the_legacy_path_is_still_reported_while_it_is_in_use

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

`_default_database_path` stays pure: it reports, it does not move.

## Location

`backend/tests/test_legacy_data_migration.py:213`

## Signature

```python
(local_app_data)
```

## Parameters

- `local_app_data`

## Calls

- [[backend.app.config._default_database_path|_default_database_path]] (calls)

## Side Effects

- none statically observed
