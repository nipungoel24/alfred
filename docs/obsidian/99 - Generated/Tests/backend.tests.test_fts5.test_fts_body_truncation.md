---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_fts5
qualified_name: backend.tests.test_fts5.test_fts_body_truncation
source: backend/tests/test_fts5.py
line: 82
status: active
tags: [test, function, test]
---

# test_fts_body_truncation

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

FTS5 should handle long bodies by truncating to 5000 chars.

## Location

`backend/tests/test_fts5.py:82`

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
