---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.providers.base.MailProvider
qualified_name: backend.app.mail.providers.base.MailProvider.send_draft_reply
source: backend/app/mail/providers/base.py
line: 25
status: active
tags: [gmail, function]
---

# send_draft_reply

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Sends a reply to an existing email thread.

## Location

`backend/app/mail/providers/base.py:25`

## Signature

```python
(self, account: EmailAccount, credentials: Dict[str, Any], original_email: Email, reply_body: str) -> Dict[str, Any]
```

## Parameters

- `self`
- `account` (`EmailAccount`)
- `credentials` (`Dict[str, Any]`)
- `original_email` (`Email`)
- `reply_body` (`str`)

## Returns

`Dict[str, Any]`

## Side Effects

- async I/O
