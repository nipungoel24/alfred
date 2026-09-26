---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_structured_search
qualified_name: backend.tests.test_structured_search.test_global_free_text_finds_body_only_word
source: backend/tests/test_structured_search.py
line: 252
status: active
tags: [test, function, test]
---

# test_global_free_text_finds_body_only_word

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Normal global search (free_text only) reaches the FTS/BM25 path:

## Location

`backend/tests/test_structured_search.py:252`

## Signature

```python
(isolated_app)
```

## Parameters

- `isolated_app`

## Calls

- `TestClient` (`fastapi.testclient.TestClient`, calls-inferred)

## Side Effects

- network (HTTP)
