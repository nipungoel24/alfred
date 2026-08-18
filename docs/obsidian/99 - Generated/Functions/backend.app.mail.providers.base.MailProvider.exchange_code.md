---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.providers.base.MailProvider
qualified_name: backend.app.mail.providers.base.MailProvider.exchange_code
source: backend/app/mail/providers/base.py
line: 9
status: active
tags: [gmail, function]
---

# exchange_code

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Exchanges authorization code for access and refresh tokens.

## Location

`backend/app/mail/providers/base.py:9`

## Signature

```python
(self, code: str, redirect_uri: str) -> Dict[str, Any]
```

## Parameters

- `self`
- `code` (`str`)
- `redirect_uri` (`str`)

## Returns

`Dict[str, Any]`

## Side Effects

- async I/O
