---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_fts5
qualified_name: backend.tests.test_fts5.test_fts_rebuild_removes_orphans
source: backend/tests/test_fts5.py
line: 181
status: active
tags: [test, function, test]
---

# test_fts_rebuild_removes_orphans

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Rebuild should remove orphaned FTS entries.

## Location

`backend/tests/test_fts5.py:181`

## Signature

```python
(tmp_path: Path)
```

## Parameters

- `tmp_path` (`Path`)

## Calls

- [[backend.app.db.repositories.Repository|Repository]] (calls)

## Writes

- [[table_emails]]

## Side Effects

- SQLite
