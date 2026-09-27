---
type: function
generated: true
language: python
layer: database
module: backend.app.db.database
qualified_name: backend.app.db.database._migrate
source: backend/app/db/database.py
line: 344
status: active
tags: [database, function]
---

# _migrate

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Run incremental schema migrations for legacy databases.

## Location

`backend/app/db/database.py:344`

## Signature

```python
(connection: sqlite3.Connection)
```

## Parameters

- `connection` (`sqlite3.Connection`)

## Calls

- `Path` (`pathlib.Path`, calls-inferred)

## Reads

- [[table_emails]]
- [[table_tasks]]

## Writes

- [[table_email_analysis]]
- [[table_emails]]
- [[table_jobs]]
- [[table_tasks]]

## Side Effects

- SQLite
