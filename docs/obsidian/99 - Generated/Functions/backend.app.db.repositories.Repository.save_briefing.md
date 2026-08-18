---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.save_briefing
source: backend/app/db/repositories.py
line: 418
status: active
tags: [database, function]
---

# save_briefing

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `save_briefing` in `backend/app/db/repositories.py`.

## Location

`backend/app/db/repositories.py:418`

## Signature

```python
(self, fingerprint: str, model: str, briefing: InboxBriefing, schema = '1')
```

## Parameters

- `self`
- `fingerprint` (`str`)
- `model` (`str`)
- `briefing` (`InboxBriefing`)
- `schema`

## Calls

- `now` (`datetime.datetime.now`, calls-inferred)

## Writes

- [[table_inbox_briefing]]

## Side Effects

- SQLite
