---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.providers.gmail.GmailProvider
qualified_name: backend.app.mail.providers.gmail.GmailProvider._extract_body
source: backend/app/mail/providers/gmail.py
line: 533
status: active
tags: [gmail, function]
---

# _extract_body

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `_extract_body` in `backend/app/mail/providers/gmail.py`.

## Location

`backend/app/mail/providers/gmail.py:533`

## Signature

```python
(self, payload: Dict[str, Any]) -> str
```

## Parameters

- `self`
- `payload` (`Dict[str, Any]`)

## Returns

`str`

## Calls

- `urlsafe_b64decode` (`base64.urlsafe_b64decode`, calls-inferred)

## Side Effects

- none statically observed
