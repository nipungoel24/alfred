---
type: function
generated: true
language: python
layer: database
module: backend.app.db.database
qualified_name: backend.app.db.database.snapshot_database
source: backend/app/db/database.py
line: 40
status: active
tags: [database, function]
---

# snapshot_database

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

WAL-safe snapshot of a database FILE to another path.

## Location

`backend/app/db/database.py:40`

## Signature

```python
(source_path: Path, dest_path: Path)
```

## Parameters

- `source_path` (`Path`)
- `dest_path` (`Path`)

## Calls

- `connect` (`sqlite3.connect`, calls-inferred)

## Side Effects

- none statically observed
