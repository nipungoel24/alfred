---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_fts5
source: backend/tests/test_fts5.py
status: active
tags: [module, backend]
---

# backend.tests.test_fts5

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_fts5.py`

## Imports

- `Email` ← `backend.app.schemas.Email`
- `Path` ← `pathlib.Path`
- `Repository` ← `backend.app.db.repositories.Repository`
- `sqlite3` ← `sqlite3`

## Functions

- [[backend.tests.test_fts5.make_email|make_email]]

## Tests

- [[backend.tests.test_fts5.test_fts_body_truncation|test_fts_body_truncation]]
- [[backend.tests.test_fts5.test_fts_case_insensitive|test_fts_case_insensitive]]
- [[backend.tests.test_fts5.test_fts_delete_cleans_index|test_fts_delete_cleans_index]]
- [[backend.tests.test_fts5.test_fts_empty_body|test_fts_empty_body]]
- [[backend.tests.test_fts5.test_fts_fallback_to_like|test_fts_fallback_to_like]]
- [[backend.tests.test_fts5.test_fts_insert_and_search|test_fts_insert_and_search]]
- [[backend.tests.test_fts5.test_fts_insert_new_does_not_duplicate|test_fts_insert_new_does_not_duplicate]]
- [[backend.tests.test_fts5.test_fts_multiple_delete|test_fts_multiple_delete]]
- [[backend.tests.test_fts5.test_fts_multiple_emails|test_fts_multiple_emails]]
- [[backend.tests.test_fts5.test_fts_rebuild_removes_orphans|test_fts_rebuild_removes_orphans]]
- [[backend.tests.test_fts5.test_fts_search_no_match|test_fts_search_no_match]]
- [[backend.tests.test_fts5.test_fts_special_characters|test_fts_special_characters]]
- [[backend.tests.test_fts5.test_fts_update_without_manual_repair|test_fts_update_without_manual_repair]]
- [[backend.tests.test_fts5.test_fts_upsert_idempotent|test_fts_upsert_idempotent]]
