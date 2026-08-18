---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.app.mail.providers.gmail
source: backend/app/mail/providers/gmail.py
status: active
tags: [module, backend]
---

# backend.app.mail.providers.gmail

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/app/mail/providers/gmail.py`

## Imports

- `Any` ← `typing.Any`
- `Dict` ← `typing.Dict`
- `Email` ← `backend.app.schemas.Email`
- `EmailAccount` ← `backend.app.schemas.EmailAccount`
- `List` ← `typing.List`
- `MailProvider` ← `backend.app.mail.providers.base.MailProvider`
- `base64` ← `base64`
- `content_fingerprint` ← `backend.app.mail.fingerprint.content_fingerprint`
- `datetime` ← `datetime.datetime`
- `httpx` ← `httpx`
- `timedelta` ← `datetime.timedelta`
- `timezone` ← `datetime.timezone`

## Classes

- [[backend.app.mail.providers.gmail.GmailProvider|GmailProvider]]

## Functions

- [[backend.app.mail.providers.gmail.GmailProvider.__init__|__init__]]
- [[backend.app.mail.providers.gmail.GmailProvider._clean_html|_clean_html]]
- [[backend.app.mail.providers.gmail.GmailProvider._ensure_access_token|_ensure_access_token]]
- [[backend.app.mail.providers.gmail.GmailProvider._extract_body|_extract_body]]
- [[backend.app.mail.providers.gmail.GmailProvider._normalize_message|_normalize_message]]
- [[backend.app.mail.providers.gmail.GmailProvider.backfill_messages|backfill_messages]]
- [[backend.app.mail.providers.gmail.GmailProvider.exchange_code|exchange_code]]
- [[backend.app.mail.providers.gmail.GmailProvider.fetch_backfill_estimate|fetch_backfill_estimate]]
- [[backend.app.mail.providers.gmail.GmailProvider.get_auth_url|get_auth_url]]
- [[backend.app.mail.providers.gmail.GmailProvider.get_user_info|get_user_info]]
- [[backend.app.mail.providers.gmail.GmailProvider.refresh_message_labels|refresh_message_labels]]
- [[backend.app.mail.providers.gmail.GmailProvider.refresh_tokens|refresh_tokens]]
- [[backend.app.mail.providers.gmail.GmailProvider.sync_messages|sync_messages]]
