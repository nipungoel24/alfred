---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_fts_upgrade
qualified_name: backend.tests.test_fts_upgrade.test_legacy_fts_schema_upgrades_through_connect
source: backend/tests/test_fts_upgrade.py
line: 41
status: active
tags: [test, function, test]
---

# test_legacy_fts_schema_upgrades_through_connect

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Full 10-step legacy upgrade regression through production connect().

## Location

`backend/tests/test_fts_upgrade.py:41`

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

## Writes

- [[table_emails]]
- [[table_emails_fts]]

## Side Effects

- SQLite
