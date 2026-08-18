---
type: function
generated: true
language: python
layer: database
module: backend.app.db.database
qualified_name: backend.app.db.database.transaction
source: backend/app/db/database.py
line: 273
status: active
tags: [database, function]
---

# transaction

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Context manager for batched write transactions.

## Location

`backend/app/db/database.py:273`

## Signature

```python
(connection: sqlite3.Connection)
```

## Parameters

- `connection` (`sqlite3.Connection`)

## Called By

- [[backend.app.db.repositories.Repository.save_tasks_batch|save_tasks_batch]]
- [[backend.app.db.repositories.Repository.upsert_emails_batch|upsert_emails_batch]]

## Side Effects

- none statically observed
