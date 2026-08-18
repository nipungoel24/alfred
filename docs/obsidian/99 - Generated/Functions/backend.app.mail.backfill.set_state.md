---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.backfill
qualified_name: backend.app.mail.backfill.set_state
source: backend/app/mail/backfill.py
line: 68
status: active
tags: [gmail, function]
---

# set_state

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `set_state` in `backend/app/mail/backfill.py`.

## Location

`backend/app/mail/backfill.py:68`

## Signature

```python
(data: dict, state: BackfillState) -> dict
```

## Parameters

- `data` (`dict`)
- `state` (`BackfillState`)

## Returns

`dict`

## Called By

- [[backend.app.main._set_backfill_state|_set_backfill_state]]
- [[backend.app.main.backfill_account|backfill_account]]
- [[backend.app.main.pause_backfill|pause_backfill]]
- [[backend.app.main.sync_account|sync_account]]
- [[backend.tests.test_backfill_jobs.test_status_payload_complete|test_status_payload_complete]]

## Side Effects

- none statically observed
