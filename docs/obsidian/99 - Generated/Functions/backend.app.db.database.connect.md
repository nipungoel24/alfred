---
type: function
generated: true
language: python
layer: database
module: backend.app.db.database
qualified_name: backend.app.db.database.connect
source: backend/app/db/database.py
line: 128
status: active
tags: [database, function, critical-path]
---

# connect

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Create an optimized SQLite connection with WAL mode and indexes.

## Location

`backend/app/db/database.py:128`

## Signature

```python
(path: Path) -> sqlite3.Connection
```

## Parameters

- `path` (`Path`)

## Returns

`sqlite3.Connection`

## Calls

- `connect` (`sqlite3.connect`, calls-inferred)

## Called By

- [[backend.app.db.repositories.Repository.__init__|__init__]]

## Side Effects

- none statically observed
