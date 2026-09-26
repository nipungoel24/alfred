---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_structured_search
qualified_name: backend.tests.test_structured_search.test_structured_search_no_results
source: backend/tests/test_structured_search.py
line: 136
status: active
tags: [test, function, test]
---

# test_structured_search_no_results

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Should return empty when no emails match.

## Location

`backend/tests/test_structured_search.py:136`

## Signature

```python
(tmp_path: Path)
```

## Parameters

- `tmp_path` (`Path`)

## Calls

- [[backend.app.db.repositories.Repository|Repository]] (calls)
- [[backend.app.schemas.SearchFilters|SearchFilters]] (calls)

## Side Effects

- none statically observed
