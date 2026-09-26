---
type: function
generated: true
language: python
layer: database
module: backend.app.db.database
qualified_name: backend.app.db.database.repopulate_fts_index
source: backend/app/db/database.py
line: 236
status: active
tags: [database, function]
---

# repopulate_fts_index

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Re-index every email row into emails_fts (content repair).

## Location

`backend/app/db/database.py:236`

## Signature

```python
(connection: sqlite3.Connection)
```

## Parameters

- `connection` (`sqlite3.Connection`)

## Called By

- [[backend.app.db.repositories.Repository.rebuild_fts|rebuild_fts]]

## Writes

- [[table_emails_fts]]

## Side Effects

- SQLite
