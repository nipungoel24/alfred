---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.backfill
qualified_name: backend.app.mail.backfill.record_success
source: backend/app/mail/backfill.py
line: 75
status: active
tags: [gmail, function]
---

# record_success

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Update counters after one successful bounded page.

## Location

`backend/app/mail/backfill.py:75`

## Signature

```python
(data: dict, imported: int, page_token: str | None, estimate: int | None) -> dict
```

## Parameters

- `data` (`dict`)
- `imported` (`int`)
- `page_token` (`str | None`)
- `estimate` (`int | None`)

## Returns

`dict`

## Calls

- `now` (`datetime.datetime.now`, calls-inferred)

## Side Effects

- none statically observed
