---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_fts5
qualified_name: backend.tests.test_fts5.test_fts_upsert_idempotent
source: backend/tests/test_fts5.py
line: 169
status: active
tags: [test, function, test]
---

# test_fts_upsert_idempotent

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Upserting the same email twice should not create duplicates.

## Location

`backend/tests/test_fts5.py:169`

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
