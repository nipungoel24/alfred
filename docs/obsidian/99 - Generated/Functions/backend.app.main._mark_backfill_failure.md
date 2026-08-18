---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main._mark_backfill_failure
source: backend/app/main.py
line: 171
status: active
tags: [backend, function]
---

# _mark_backfill_failure

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `_mark_backfill_failure` in `backend/app/main.py`.

## Location

`backend/app/main.py:171`

## Signature

```python
(account: EmailAccount, code: str, message: str)
```

## Parameters

- `account` (`EmailAccount`)
- `code` (`str`)
- `message` (`str`)

## Calls

- [[backend.app.mail.backfill.dump_cursor|dump_cursor]] (calls)
- [[backend.app.mail.backfill.normalize_cursor|normalize_cursor]] (calls)
- [[backend.app.mail.backfill.record_failure|record_failure]] (calls)

## Side Effects

- none statically observed
