---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.providers.base.MailProvider
qualified_name: backend.app.mail.providers.base.MailProvider.sync_messages
source: backend/app/mail/providers/base.py
line: 21
status: active
tags: [gmail, function]
---

# sync_messages

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Synchronizes mailbox messages and returns counts.

## Location

`backend/app/mail/providers/base.py:21`

## Signature

```python
(self, account: EmailAccount, credentials: Dict[str, Any], repo) -> Dict[str, Any]
```

## Parameters

- `self`
- `account` (`EmailAccount`)
- `credentials` (`Dict[str, Any]`)
- `repo`

## Returns

`Dict[str, Any]`

## Side Effects

- async I/O
