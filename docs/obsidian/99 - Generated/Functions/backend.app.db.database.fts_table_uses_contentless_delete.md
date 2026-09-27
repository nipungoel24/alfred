---
type: function
generated: true
language: python
layer: database
module: backend.app.db.database
qualified_name: backend.app.db.database.fts_table_uses_contentless_delete
source: backend/app/db/database.py
line: 223
status: active
tags: [database, function]
---

# fts_table_uses_contentless_delete

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

What schema does the EXISTING emails_fts table actually use?

## Location

`backend/app/db/database.py:223`

## Signature

```python
(connection: sqlite3.Connection) -> bool | None
```

## Parameters

- `connection` (`sqlite3.Connection`)

## Returns

`bool | None`

## Called By

- [[backend.tests.test_fts_upgrade.test_existing_schema_detection|test_existing_schema_detection]]
- [[backend.tests.test_fts_upgrade.test_legacy_fts_schema_upgrades_through_connect|test_legacy_fts_schema_upgrades_through_connect]]
- [[backend.tests.test_fts_upgrade.test_old_sqlite_fallback_path|test_old_sqlite_fallback_path]]

## Side Effects

- none statically observed
