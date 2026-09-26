---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_fts_upgrade
qualified_name: backend.tests.test_fts_upgrade.test_existing_schema_detection
source: backend/tests/test_fts_upgrade.py
line: 103
status: active
tags: [test, function, test]
---

# test_existing_schema_detection

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_existing_schema_detection` in `backend/tests/test_fts_upgrade.py`.

## Location

`backend/tests/test_fts_upgrade.py:103`

## Signature

```python
(tmp_path: Path)
```

## Parameters

- `tmp_path` (`Path`)

## Calls

- [[backend.app.db.database.fts_table_uses_contentless_delete|fts_table_uses_contentless_delete]] (calls)
- [[backend.app.db.repositories.Repository|Repository]] (calls)
- `connect` (`sqlite3.connect`, calls-inferred)

## Side Effects

- none statically observed
