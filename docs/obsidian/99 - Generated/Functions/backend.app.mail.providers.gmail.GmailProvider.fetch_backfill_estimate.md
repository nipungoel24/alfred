---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.providers.gmail.GmailProvider
qualified_name: backend.app.mail.providers.gmail.GmailProvider.fetch_backfill_estimate
source: backend/app/mail/providers/gmail.py
line: 206
status: active
tags: [gmail, function]
---

# fetch_backfill_estimate

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Cheap one-shot resultSizeEstimate for the backfill query.

## Location

`backend/app/mail/providers/gmail.py:206`

## Signature

```python
(self, access_token: str) -> int | None
```

## Parameters

- `self`
- `access_token` (`str`)

## Returns

`int | None`

## Calls

- `AsyncClient` (`httpx.AsyncClient`, calls-inferred)

## Side Effects

- async I/O
