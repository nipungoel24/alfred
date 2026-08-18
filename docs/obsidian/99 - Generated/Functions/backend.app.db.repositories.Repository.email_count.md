---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.email_count
source: backend/app/db/repositories.py
line: 87
status: active
tags: [database, function]
---

# email_count

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Get total email count, optionally filtered by account.

## Location

`backend/app/db/repositories.py:87`

## Signature

```python
(self, account_id = None) -> int
```

## Parameters

- `self`
- `account_id`

## Returns

`int`

## Called By

- [[backend.tests.test_task_migration.test_migration_idempotency_and_preservation|test_migration_idempotency_and_preservation]]

## Reads

- [[table_emails]]

## Side Effects

- SQLite
