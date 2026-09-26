---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.app.db.database
source: backend/app/db/database.py
status: active
tags: [module, backend]
---

# backend.app.db.database

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/app/db/database.py`

## Imports

- `Path` ← `pathlib.Path`
- `contextmanager` ← `contextlib.contextmanager`
- `sqlite3` ← `sqlite3`

## Classes

- [[backend.app.db.database.MigrationSafetyError|MigrationSafetyError]]

## Functions

- [[backend.app.db.database._migrate|_migrate]]
- [[backend.app.db.database._sqlite_backup|_sqlite_backup]]
- [[backend.app.db.database.connect|connect]]
- [[backend.app.db.database.ensure_fts_schema|ensure_fts_schema]]
- [[backend.app.db.database.fts_delete_supported|fts_delete_supported]]
- [[backend.app.db.database.fts_table_uses_contentless_delete|fts_table_uses_contentless_delete]]
- [[backend.app.db.database.repopulate_fts_index|repopulate_fts_index]]
- [[backend.app.db.database.snapshot_database|snapshot_database]]
- [[backend.app.db.database.transaction|transaction]]

## Constants

- `FTS_SCHEMA`
- `FTS_SCHEMA_LEGACY`
- `INDEXES`
- `SCHEMA`
