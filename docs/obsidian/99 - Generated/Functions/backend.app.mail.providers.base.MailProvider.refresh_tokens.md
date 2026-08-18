---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.providers.base.MailProvider
qualified_name: backend.app.mail.providers.base.MailProvider.refresh_tokens
source: backend/app/mail/providers/base.py
line: 13
status: active
tags: [gmail, function]
---

# refresh_tokens

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Uses refresh token to get a new access token.

## Location

`backend/app/mail/providers/base.py:13`

## Signature

```python
(self, refresh_token: str) -> Dict[str, Any]
```

## Parameters

- `self`
- `refresh_token` (`str`)

## Returns

`Dict[str, Any]`

## Side Effects

- async I/O; handles credentials/tokens — see [[Token Security]]
