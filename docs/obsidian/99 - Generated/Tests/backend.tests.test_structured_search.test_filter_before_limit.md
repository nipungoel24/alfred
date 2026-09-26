---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_structured_search
qualified_name: backend.tests.test_structured_search.test_filter_before_limit
source: backend/tests/test_structured_search.py
line: 167
status: active
tags: [test, function, test]
---

# test_filter_before_limit

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Priority and needs_reply filters must be applied BEFORE LIMIT/OFFSET.

## Location

`backend/tests/test_structured_search.py:167`

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
