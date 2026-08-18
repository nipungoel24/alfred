---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.providers.base.MailProvider
qualified_name: backend.app.mail.providers.base.MailProvider.get_user_info
source: backend/app/mail/providers/base.py
line: 17
status: active
tags: [gmail, function]
---

# get_user_info

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Retrieves user account info (email, name).

## Location

`backend/app/mail/providers/base.py:17`

## Signature

```python
(self, access_token: str) -> Dict[str, Any]
```

## Parameters

- `self`
- `access_token` (`str`)

## Returns

`Dict[str, Any]`

## Side Effects

- async I/O
