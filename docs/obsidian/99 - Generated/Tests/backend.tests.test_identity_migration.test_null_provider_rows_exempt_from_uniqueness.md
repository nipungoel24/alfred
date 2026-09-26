---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_identity_migration
qualified_name: backend.tests.test_identity_migration.test_null_provider_rows_exempt_from_uniqueness
source: backend/tests/test_identity_migration.py
line: 253
status: active
tags: [test, function, test]
---

# test_null_provider_rows_exempt_from_uniqueness

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Legacy/CSV rows with NULL provider ids never collide.

## Location

`backend/tests/test_identity_migration.py:253`

## Signature

```python
(tmp_path: Path)
```

## Parameters

- `tmp_path` (`Path`)

## Calls

- [[backend.app.db.repositories.Repository|Repository]] (calls)
- [[backend.app.schemas.Email|Email]] (calls)

## Side Effects

- none statically observed
