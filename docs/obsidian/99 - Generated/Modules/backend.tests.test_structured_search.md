---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_structured_search
source: backend/tests/test_structured_search.py
status: active
tags: [module, backend]
---

# backend.tests.test_structured_search

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_structured_search.py`

## Imports

- `Email` ← `backend.app.schemas.Email`
- `Path` ← `pathlib.Path`
- `Repository` ← `backend.app.db.repositories.Repository`
- `SearchFilters` ← `backend.app.schemas.SearchFilters`
- `TestClient` ← `fastapi.testclient.TestClient`
- `pytest` ← `pytest`

## Functions

- [[backend.tests.test_structured_search._seed_search_mail|_seed_search_mail]]
- [[backend.tests.test_structured_search.isolated_app|isolated_app]]
- [[backend.tests.test_structured_search.make_email|make_email]]
- [[backend.tests.test_structured_search.test_in_scope_mapping.search|search]]

## Tests

- [[backend.tests.test_structured_search.test_account_scoped_structured_search|test_account_scoped_structured_search]]
- [[backend.tests.test_structured_search.test_filter_before_limit|test_filter_before_limit]]
- [[backend.tests.test_structured_search.test_global_free_text_finds_body_only_word|test_global_free_text_finds_body_only_word]]
- [[backend.tests.test_structured_search.test_in_scope_mapping|test_in_scope_mapping]]
- [[backend.tests.test_structured_search.test_in_scope_unknown_rejected|test_in_scope_unknown_rejected]]
- [[backend.tests.test_structured_search.test_structured_search_by_date|test_structured_search_by_date]]
- [[backend.tests.test_structured_search.test_structured_search_by_sender|test_structured_search_by_sender]]
- [[backend.tests.test_structured_search.test_structured_search_by_subject|test_structured_search_by_subject]]
- [[backend.tests.test_structured_search.test_structured_search_combined_filters|test_structured_search_combined_filters]]
- [[backend.tests.test_structured_search.test_structured_search_limit|test_structured_search_limit]]
- [[backend.tests.test_structured_search.test_structured_search_no_results|test_structured_search_no_results]]
- [[backend.tests.test_structured_search.test_structured_search_with_free_text|test_structured_search_with_free_text]]
