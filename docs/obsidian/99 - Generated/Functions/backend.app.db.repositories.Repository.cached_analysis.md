---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.cached_analysis
source: backend/app/db/repositories.py
line: 373
status: active
tags: [database, function]
---

# cached_analysis

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `cached_analysis` in `backend/app/db/repositories.py`.

## Location

`backend/app/db/repositories.py:373`

## Signature

```python
(self, email_id: str, fingerprint: str, model: str, schema = '1')
```

## Parameters

- `self`
- `email_id` (`str`)
- `fingerprint` (`str`)
- `model` (`str`)
- `schema`

## Calls

- `model_validate_json` (`backend.app.schemas.EmailAnalysis.model_validate_json`, calls-inferred)

## Reads

- [[table_email_analysis]]

## Side Effects

- SQLite
