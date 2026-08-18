---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.backfill
qualified_name: backend.app.mail.backfill.dump_cursor
source: backend/app/mail/backfill.py
line: 64
status: active
tags: [gmail, function]
---

# dump_cursor

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `dump_cursor` in `backend/app/mail/backfill.py`.

## Location

`backend/app/mail/backfill.py:64`

## Signature

```python
(data: dict) -> str
```

## Parameters

- `data` (`dict`)

## Returns

`str`

## Calls

- `dumps` (`json.dumps`, calls-inferred)

## Called By

- [[backend.app.main._backfill_estimate_once|_backfill_estimate_once]]
- [[backend.app.main._mark_backfill_failure|_mark_backfill_failure]]
- [[backend.app.main._set_backfill_state|_set_backfill_state]]
- [[backend.app.main.backfill_account|backfill_account]]
- [[backend.app.main.pause_backfill|pause_backfill]]
- [[backend.app.main.sync_account|sync_account]]

## Side Effects

- none statically observed
