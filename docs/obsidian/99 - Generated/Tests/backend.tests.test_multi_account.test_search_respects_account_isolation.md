---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_multi_account
qualified_name: backend.tests.test_multi_account.test_search_respects_account_isolation
source: backend/tests/test_multi_account.py
line: 98
status: active
tags: [test, function, test]
---

# test_search_respects_account_isolation

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Search should work across accounts but preserve account context.

## Location

`backend/tests/test_multi_account.py:98`

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
