---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.rebuild_fts
source: backend/app/db/repositories.py
line: 583
status: active
tags: [database, function]
---

# rebuild_fts

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Rebuild the FTS5 index from the emails table.

## Location

`backend/app/db/repositories.py:583`

## Signature

```python
(self)
```

## Parameters

- `self`

## Calls

- [[backend.app.db.database.fts_delete_supported|fts_delete_supported]] (calls)
- [[backend.app.db.database.repopulate_fts_index|repopulate_fts_index]] (calls)
- `getLogger` (`logging.getLogger`, calls-inferred)

## Side Effects

- none statically observed
