---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.providers.gmail.GmailProvider
qualified_name: backend.app.mail.providers.gmail.GmailProvider.exchange_code
source: backend/app/mail/providers/gmail.py
line: 38
status: active
tags: [gmail, function]
---

# exchange_code

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `exchange_code` in `backend/app/mail/providers/gmail.py`.

## Location

`backend/app/mail/providers/gmail.py:38`

## Signature

```python
(self, code: str, redirect_uri: str, code_verifier: str) -> Dict[str, Any]
```

## Parameters

- `self`
- `code` (`str`)
- `redirect_uri` (`str`)
- `code_verifier` (`str`)

## Returns

`Dict[str, Any]`

## Calls

- `AsyncClient` (`httpx.AsyncClient`, calls-inferred)

## Side Effects

- async I/O
