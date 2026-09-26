---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_identity_migration
qualified_name: backend.tests.test_identity_migration.test_migration_rekeys_legacy_database
source: backend/tests/test_identity_migration.py
line: 64
status: active
tags: [test, function, test]
---

# test_migration_rekeys_legacy_database

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Old raw-Gmail-ID database migrates losslessly.

## Location

`backend/tests/test_identity_migration.py:64`

## Signature

```python
(tmp_path: Path)
```

## Parameters

- `tmp_path` (`Path`)

## Calls

- [[backend.app.db.repositories.Repository|Repository]] (calls)
- [[backend.app.mail.identity.scoped_email_id|scoped_email_id]] (calls)
- [[backend.app.schemas.EmailAnalysis|EmailAnalysis]] (calls)
- `connect` (`sqlite3.connect`, calls-inferred)

## Writes

- [[table_email_analysis]]
- [[table_emails]]
- [[table_emails_fts]]
- [[table_jobs]]
- [[table_tasks]]

## Side Effects

- SQLite
