---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.providers.base.MailProvider
qualified_name: backend.app.mail.providers.base.MailProvider.get_auth_url
source: backend/app/mail/providers/base.py
line: 5
status: active
tags: [gmail, function]
---

# get_auth_url

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Returns the authorization URL to start the OAuth flow.

## Location

`backend/app/mail/providers/base.py:5`

## Signature

```python
(self, redirect_uri: str) -> str
```

## Parameters

- `self`
- `redirect_uri` (`str`)

## Returns

`str`

## Side Effects

- async I/O
