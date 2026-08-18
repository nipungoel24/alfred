---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.cached_briefing
source: backend/app/db/repositories.py
line: 411
status: active
tags: [database, function]
---

# cached_briefing

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `cached_briefing` in `backend/app/db/repositories.py`.

## Location

`backend/app/db/repositories.py:411`

## Signature

```python
(self, fingerprint: str, model: str, schema = '1')
```

## Parameters

- `self`
- `fingerprint` (`str`)
- `model` (`str`)
- `schema`

## Calls

- `model_validate_json` (`backend.app.schemas.InboxBriefing.model_validate_json`, calls-inferred)

## Reads

- [[table_inbox_briefing]]

## Side Effects

- SQLite
