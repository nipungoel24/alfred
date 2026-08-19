---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.providers.gmail.GmailProvider
qualified_name: backend.app.mail.providers.gmail.GmailProvider.refresh_message_labels
source: backend/app/mail/providers/gmail.py
line: 75
status: active
tags: [gmail, function]
---

# refresh_message_labels

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Fetch ONLY the current label set of a message (format=METADATA).

## Location

`backend/app/mail/providers/gmail.py:75`

## Signature

```python
(self, access_token: str, msg_id: str) -> list[str] | None
```

## Parameters

- `self`
- `access_token` (`str`)
- `msg_id` (`str`)

## Returns

`list[str] | None`

## Calls

- `AsyncClient` (`httpx.AsyncClient`, calls-inferred)

## Side Effects

- async I/O
