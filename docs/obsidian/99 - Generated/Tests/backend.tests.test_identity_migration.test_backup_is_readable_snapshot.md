---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_identity_migration
qualified_name: backend.tests.test_identity_migration.test_backup_is_readable_snapshot
source: backend/tests/test_identity_migration.py
line: 165
status: active
tags: [test, function, test]
---

# test_backup_is_readable_snapshot

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

The pre-migration backup opens cleanly and holds pre-migration data.

## Location

`backend/tests/test_identity_migration.py:165`

## Signature

```python
(tmp_path: Path)
```

## Parameters

- `tmp_path` (`Path`)

## Calls

- [[backend.app.db.repositories.Repository|Repository]] (calls)
- [[backend.app.schemas.Email|Email]] (calls)
- `loads` (`json.loads`, calls-inferred)
- `connect` (`sqlite3.connect`, calls-inferred)

## Reads

- [[table_emails]]

## Side Effects

- SQLite
