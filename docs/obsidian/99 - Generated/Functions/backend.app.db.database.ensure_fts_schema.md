---
type: function
generated: true
language: python
layer: database
module: backend.app.db.database
qualified_name: backend.app.db.database.ensure_fts_schema
source: backend/app/db/database.py
line: 248
status: active
tags: [database, function]
---

# ensure_fts_schema

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Idempotent FTS schema + content guarantee, run on every connect().

## Location

`backend/app/db/database.py:248`

## Signature

```python
(connection: sqlite3.Connection)
```

## Parameters

- `connection` (`sqlite3.Connection`)

## Reads

- [[table_emails]]
- [[table_emails_fts]]

## Side Effects

- SQLite
