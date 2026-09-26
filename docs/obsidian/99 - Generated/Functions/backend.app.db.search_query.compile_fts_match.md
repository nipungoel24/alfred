---
type: function
generated: true
language: python
layer: database
module: backend.app.db.search_query
qualified_name: backend.app.db.search_query.compile_fts_match
source: backend/app/db/search_query.py
line: 15
status: active
tags: [database, function]
---

# compile_fts_match

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Compile free-text words into a deterministic safe FTS5 MATCH string.

## Location

`backend/app/db/search_query.py:15`

## Signature

```python
(words: list[str] | tuple[str, ...] | None) -> str | None
```

## Parameters

- `words` (`list[str] | tuple[str, ...] | None`)

## Returns

`str | None`

## Called By

- [[backend.app.db.repositories.Repository.search_emails|search_emails]]
- [[backend.app.db.repositories.Repository.search_emails_structured|search_emails_structured]]
- [[backend.tests.test_fts_upgrade.test_compile_empty|test_compile_empty]]
- [[backend.tests.test_fts_upgrade.test_compile_plain_words|test_compile_plain_words]]
- [[backend.tests.test_fts_upgrade.test_compile_special_characters_stay_literal|test_compile_special_characters_stay_literal]]

## Side Effects

- none statically observed
