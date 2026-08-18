---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.backfill
qualified_name: backend.app.mail.backfill.record_failure
source: backend/app/mail/backfill.py
line: 88
status: active
tags: [gmail, function]
---

# record_failure

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `record_failure` in `backend/app/mail/backfill.py`.

## Location

`backend/app/mail/backfill.py:88`

## Signature

```python
(data: dict, error_code: str, error_message: str) -> dict
```

## Parameters

- `data` (`dict`)
- `error_code` (`str`)
- `error_message` (`str`)

## Returns

`dict`

## Called By

- [[backend.app.main._mark_backfill_failure|_mark_backfill_failure]]

## Side Effects

- none statically observed
