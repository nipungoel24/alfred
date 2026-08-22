---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main._set_backfill_state
source: backend/app/main.py
line: 165
status: active
tags: [backend, function]
---

# _set_backfill_state

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `_set_backfill_state` in `backend/app/main.py`.

## Location

`backend/app/main.py:165`

## Signature

```python
(account: EmailAccount, state: BackfillState)
```

## Parameters

- `account` (`EmailAccount`)
- `state` (`BackfillState`)

## Calls

- [[backend.app.mail.backfill.dump_cursor|dump_cursor]] (calls)
- [[backend.app.mail.backfill.normalize_cursor|normalize_cursor]] (calls)
- [[backend.app.mail.backfill.set_state|set_state]] (calls)

## Side Effects

- none statically observed
