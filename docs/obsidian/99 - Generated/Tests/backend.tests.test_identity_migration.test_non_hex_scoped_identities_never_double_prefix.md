---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_identity_migration
qualified_name: backend.tests.test_identity_migration.test_non_hex_scoped_identities_never_double_prefix
source: backend/tests/test_identity_migration.py
line: 263
status: active
tags: [test, function, test]
---

# test_non_hex_scoped_identities_never_double_prefix

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Already-scoped ids with non-hex provider suffixes must survive

## Location

`backend/tests/test_identity_migration.py:263`

## Signature

```python
(tmp_path: Path)
```

## Parameters

- `tmp_path` (`Path`)

## Calls

- [[backend.app.db.repositories.Repository|Repository]] (calls)
- [[backend.app.mail.identity.is_scoped_for|is_scoped_for]] (calls)
- [[backend.app.schemas.Email|Email]] (calls)

## Reads

- [[table_emails]]

## Side Effects

- SQLite
