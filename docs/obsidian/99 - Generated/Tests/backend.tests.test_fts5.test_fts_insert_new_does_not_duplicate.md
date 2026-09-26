---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_fts5
qualified_name: backend.tests.test_fts5.test_fts_insert_new_does_not_duplicate
source: backend/tests/test_fts5.py
line: 230
status: active
tags: [test, function, test]
---

# test_fts_insert_new_does_not_duplicate

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Inserting a new email should not create duplicate FTS entries.

## Location

`backend/tests/test_fts5.py:230`

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
