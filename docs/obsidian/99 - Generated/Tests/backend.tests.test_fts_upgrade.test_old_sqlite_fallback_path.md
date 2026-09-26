---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_fts_upgrade
qualified_name: backend.tests.test_fts_upgrade.test_old_sqlite_fallback_path
source: backend/tests/test_fts_upgrade.py
line: 117
status: active
tags: [test, function, test]
---

# test_old_sqlite_fallback_path

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Simulated incapable runtime: legacy schema + rebuild maintenance.

## Location

`backend/tests/test_fts_upgrade.py:117`

## Signature

```python
(tmp_path: Path, monkeypatch)
```

## Parameters

- `tmp_path` (`Path`)
- `monkeypatch`

## Calls

- [[backend.app.db.database.fts_table_uses_contentless_delete|fts_table_uses_contentless_delete]] (calls)
- [[backend.app.db.repositories.Repository|Repository]] (calls)

## Side Effects

- none statically observed
