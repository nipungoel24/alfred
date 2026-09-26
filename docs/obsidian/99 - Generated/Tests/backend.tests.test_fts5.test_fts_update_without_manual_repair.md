---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_fts5
qualified_name: backend.tests.test_fts5.test_fts_update_without_manual_repair
source: backend/tests/test_fts5.py
line: 203
status: active
tags: [test, function, test]
---

# test_fts_update_without_manual_repair

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Upserting an email with changed content should automatically reindex FTS.

## Location

`backend/tests/test_fts5.py:203`

## Signature

```python
(tmp_path: Path)
```

## Parameters

- `tmp_path` (`Path`)

## Calls

- [[backend.app.db.repositories.Repository|Repository]] (calls)

## Side Effects

- none statically observed
