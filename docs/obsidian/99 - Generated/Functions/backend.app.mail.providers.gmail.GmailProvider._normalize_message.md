---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.providers.gmail.GmailProvider
qualified_name: backend.app.mail.providers.gmail.GmailProvider._normalize_message
source: backend/app/mail/providers/gmail.py
line: 467
status: active
tags: [gmail, function]
---

# _normalize_message

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `_normalize_message` in `backend/app/mail/providers/gmail.py`.

## Location

`backend/app/mail/providers/gmail.py:467`

## Signature

```python
(self, detail: Dict[str, Any], account_id: str) -> Email
```

## Parameters

- `self`
- `detail` (`Dict[str, Any]`)
- `account_id` (`str`)

## Returns

`Email`

## Calls

- [[backend.app.schemas.Email|Email]] (calls)
- `fromtimestamp` (`datetime.datetime.fromtimestamp`, calls-inferred)

## Side Effects

- none statically observed
