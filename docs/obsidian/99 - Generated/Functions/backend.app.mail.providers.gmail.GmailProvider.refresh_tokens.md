---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.providers.gmail.GmailProvider
qualified_name: backend.app.mail.providers.gmail.GmailProvider.refresh_tokens
source: backend/app/mail/providers/gmail.py
line: 55
status: active
tags: [gmail, function]
---

# refresh_tokens

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `refresh_tokens` in `backend/app/mail/providers/gmail.py`.

## Location

`backend/app/mail/providers/gmail.py:55`

## Signature

```python
(self, refresh_token: str) -> Dict[str, Any]
```

## Parameters

- `self`
- `refresh_token` (`str`)

## Returns

`Dict[str, Any]`

## Calls

- `AsyncClient` (`httpx.AsyncClient`, calls-inferred)

## Side Effects

- async I/O; handles credentials/tokens — see [[Token Security]]
