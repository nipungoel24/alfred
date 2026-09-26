---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_identity_migration
qualified_name: backend.tests.test_identity_migration.test_migration_is_idempotent
source: backend/tests/test_identity_migration.py
line: 136
status: active
tags: [test, function, test]
---

# test_migration_is_idempotent

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Re-running connect() must not re-scope or double-prefix ids.

## Location

`backend/tests/test_identity_migration.py:136`

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

## Reads

- [[table_emails]]

## Side Effects

- SQLite
