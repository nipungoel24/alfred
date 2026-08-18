---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.providers.gmail.GmailProvider
qualified_name: backend.app.mail.providers.gmail.GmailProvider.get_user_info
source: backend/app/mail/providers/gmail.py
line: 64
status: active
tags: [gmail, function]
---

# get_user_info

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `get_user_info` in `backend/app/mail/providers/gmail.py`.

## Location

`backend/app/mail/providers/gmail.py:64`

## Signature

```python
(self, access_token: str) -> Dict[str, Any]
```

## Parameters

- `self`
- `access_token` (`str`)

## Returns

`Dict[str, Any]`

## Calls

- `AsyncClient` (`httpx.AsyncClient`, calls-inferred)

## Side Effects

- async I/O
