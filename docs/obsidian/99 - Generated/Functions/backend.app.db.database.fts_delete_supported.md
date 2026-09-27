---
type: function
generated: true
language: python
layer: database
module: backend.app.db.database
qualified_name: backend.app.db.database.fts_delete_supported
source: backend/app/db/database.py
line: 193
status: active
tags: [database, function]
---

# fts_delete_supported

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Does the RUNTIME SQLite support contentless_delete=1?

## Location

`backend/app/db/database.py:193`

## Signature

```python
(connection: sqlite3.Connection) -> bool
```

## Parameters

- `connection` (`sqlite3.Connection`)

## Returns

`bool`

## Called By

- [[backend.app.db.repositories.Repository._update_fts_one|_update_fts_one]]
- [[backend.app.db.repositories.Repository.delete_email|delete_email]]
- [[backend.app.db.repositories.Repository.rebuild_fts|rebuild_fts]]
- [[backend.tests.test_fts_upgrade.test_capability_probe_is_isolated|test_capability_probe_is_isolated]]

## Side Effects

- none statically observed
