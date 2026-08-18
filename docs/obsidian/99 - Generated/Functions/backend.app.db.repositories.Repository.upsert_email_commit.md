---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.upsert_email_commit
source: backend/app/db/repositories.py
line: 62
status: active
tags: [database, function]
---

# upsert_email_commit

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Insert or update a single email with immediate commit.

## Location

`backend/app/db/repositories.py:62`

## Signature

```python
(self, email: Email, fingerprint: str)
```

## Parameters

- `self`
- `email` (`Email`)
- `fingerprint` (`str`)

## Called By

- [[backend.tests.test_task_migration.test_migration_idempotency_and_preservation|test_migration_idempotency_and_preservation]]
- [[backend.tests.test_task_migration.test_migration_rollback|test_migration_rollback]]

## Side Effects

- none statically observed
