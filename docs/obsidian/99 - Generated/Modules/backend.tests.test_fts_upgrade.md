---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_fts_upgrade
source: backend/tests/test_fts_upgrade.py
status: active
tags: [module, backend]
---

# backend.tests.test_fts_upgrade

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_fts_upgrade.py`

## Imports

- `Email` ← `backend.app.schemas.Email`
- `Path` ← `pathlib.Path`
- `Repository` ← `backend.app.db.repositories.Repository`
- `SearchFilters` ← `backend.app.schemas.SearchFilters`
- `compile_fts_match` ← `backend.app.db.search_query.compile_fts_match`
- `connect` ← `backend.app.db.database.connect`
- `fts_delete_supported` ← `backend.app.db.database.fts_delete_supported`
- `fts_table_uses_contentless_delete` ← `backend.app.db.database.fts_table_uses_contentless_delete`
- `pytest` ← `pytest`
- `sqlite3` ← `sqlite3`

## Functions

- [[backend.tests.test_fts_upgrade.make_email|make_email]]

## Tests

- [[backend.tests.test_fts_upgrade.test_capability_probe_is_isolated|test_capability_probe_is_isolated]]
- [[backend.tests.test_fts_upgrade.test_compile_empty|test_compile_empty]]
- [[backend.tests.test_fts_upgrade.test_compile_plain_words|test_compile_plain_words]]
- [[backend.tests.test_fts_upgrade.test_compile_special_characters_stay_literal|test_compile_special_characters_stay_literal]]
- [[backend.tests.test_fts_upgrade.test_existing_schema_detection|test_existing_schema_detection]]
- [[backend.tests.test_fts_upgrade.test_legacy_fts_schema_upgrades_through_connect|test_legacy_fts_schema_upgrades_through_connect]]
- [[backend.tests.test_fts_upgrade.test_old_sqlite_fallback_path|test_old_sqlite_fallback_path]]
- [[backend.tests.test_fts_upgrade.test_special_characters_search_literally|test_special_characters_search_literally]]

## Constants

- `LEGACY_FTS`
