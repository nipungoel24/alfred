---
type: function
generated: true
language: python
layer: database
module: backend.app.db.database
qualified_name: backend.app.db.database._migrate
source: backend/app/db/database.py
line: 163
status: active
tags: [database, function]
---

# _migrate

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Run incremental schema migrations for legacy databases.

## Location

`backend/app/db/database.py:163`

## Signature

```python
(connection: sqlite3.Connection)
```

## Parameters

- `connection` (`sqlite3.Connection`)

## Reads

- [[table_emails]]

## Writes

- [[table_emails]]

## Side Effects

- SQLite
