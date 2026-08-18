---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.providers.gmail.GmailProvider
qualified_name: backend.app.mail.providers.gmail.GmailProvider.get_auth_url
source: backend/app/mail/providers/gmail.py
line: 18
status: active
tags: [gmail, function]
---

# get_auth_url

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `get_auth_url` in `backend/app/mail/providers/gmail.py`.

## Location

`backend/app/mail/providers/gmail.py:18`

## Signature

```python
(self, redirect_uri: str, state: str, code_challenge: str) -> str
```

## Parameters

- `self`
- `redirect_uri` (`str`)
- `state` (`str`)
- `code_challenge` (`str`)

## Returns

`str`

## Calls

- `URL` (`httpx.URL`, calls-inferred)

## Side Effects

- async I/O
