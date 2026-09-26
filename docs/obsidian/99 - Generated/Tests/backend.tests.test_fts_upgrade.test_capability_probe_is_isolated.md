---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_fts_upgrade
qualified_name: backend.tests.test_fts_upgrade.test_capability_probe_is_isolated
source: backend/tests/test_fts_upgrade.py
line: 93
status: active
tags: [test, function, test]
---

# test_capability_probe_is_isolated

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

The probe must not touch the production table name.

## Location

`backend/tests/test_fts_upgrade.py:93`

## Signature

```python
(tmp_path: Path)
```

## Parameters

- `tmp_path` (`Path`)

## Calls

- [[backend.app.db.database.fts_delete_supported|fts_delete_supported]] (calls)
- [[backend.app.db.repositories.Repository|Repository]] (calls)

## Side Effects

- none statically observed
