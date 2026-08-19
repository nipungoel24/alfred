---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.providers.gmail.GmailProvider
qualified_name: backend.app.mail.providers.gmail.GmailProvider.backfill_messages
source: backend/app/mail/providers/gmail.py
line: 121
status: active
tags: [gmail, function, critical-path]
---

# backfill_messages

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Progressive All Mail backfill — ONE bounded page per call.

## Location

`backend/app/mail/providers/gmail.py:121`

## Signature

```python
(self, account: EmailAccount, credentials: Dict[str, Any], repo, page_size: int = 40) -> Dict[str, Any]
```

## Parameters

- `self`
- `account` (`EmailAccount`)
- `credentials` (`Dict[str, Any]`)
- `repo`
- `page_size` (`int`)

## Returns

`Dict[str, Any]`

## Calls

- [[backend.app.db.repositories.Repository.email_exists|email_exists]] (calls)
- [[backend.app.db.repositories.Repository.save_account|save_account]] (calls)
- [[backend.app.db.repositories.Repository.update_email_labels|update_email_labels]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)
- [[backend.app.mail.fingerprint.content_fingerprint|content_fingerprint]] (calls)
- `AsyncClient` (`httpx.AsyncClient`, calls-inferred)

## Reads

- [[table_emails]]

## Writes

- [[table_accounts]]
- [[table_emails]]

## Side Effects

- async I/O; SQLite
