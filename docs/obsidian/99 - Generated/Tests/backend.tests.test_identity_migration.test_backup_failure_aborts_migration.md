---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_identity_migration
qualified_name: backend.tests.test_identity_migration.test_backup_failure_aborts_migration
source: backend/tests/test_identity_migration.py
line: 193
status: active
tags: [test, function, test]
---

# test_backup_failure_aborts_migration

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Fail-closed: no snapshot -> MigrationSafetyError, ids untouched,

## Location

`backend/tests/test_identity_migration.py:193`

## Signature

```python
(tmp_path: Path)
```

## Parameters

- `tmp_path` (`Path`)

## Calls

- [[backend.app.db.repositories.Repository|Repository]] (calls)
- [[backend.app.mail.identity.scoped_email_id|scoped_email_id]] (calls)
- [[backend.app.schemas.Email|Email]] (calls)
- `raises` (`pytest.raises`, calls-inferred)

## Reads

- [[table_emails]]

## Side Effects

- SQLite
