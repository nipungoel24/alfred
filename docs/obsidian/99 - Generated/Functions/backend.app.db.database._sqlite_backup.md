---
type: function
generated: true
language: python
layer: database
module: backend.app.db.database
qualified_name: backend.app.db.database._sqlite_backup
source: backend/app/db/database.py
line: 23
status: active
tags: [database, function]
---

# _sqlite_backup

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Write a consistent snapshot of `source` to `backup_file`.

## Location

`backend/app/db/database.py:23`

## Signature

```python
(source: sqlite3.Connection, backup_file: Path)
```

## Parameters

- `source` (`sqlite3.Connection`)
- `backup_file` (`Path`)

## Calls

- `connect` (`sqlite3.connect`, calls-inferred)

## Side Effects

- none statically observed
