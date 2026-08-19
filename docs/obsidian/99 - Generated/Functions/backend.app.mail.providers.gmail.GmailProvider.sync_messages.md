---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.providers.gmail.GmailProvider
qualified_name: backend.app.mail.providers.gmail.GmailProvider.sync_messages
source: backend/app/mail/providers/gmail.py
line: 230
status: active
tags: [gmail, function, critical-path]
---

# sync_messages

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `sync_messages` in `backend/app/mail/providers/gmail.py`.

## Location

`backend/app/mail/providers/gmail.py:230`

## Signature

```python
(self, account: EmailAccount, credentials: Dict[str, Any], repo, load_older: bool = False) -> Dict[str, Any]
```

## Parameters

- `self`
- `account` (`EmailAccount`)
- `credentials` (`Dict[str, Any]`)
- `repo`
- `load_older` (`bool`)

## Returns

`Dict[str, Any]`

## Calls

- [[backend.app.db.repositories.Repository.email|email]] (calls)
- [[backend.app.db.repositories.Repository.email_exists|email_exists]] (calls)
- [[backend.app.db.repositories.Repository.mark_email_excluded|mark_email_excluded]] (calls)
- [[backend.app.db.repositories.Repository.save_account|save_account]] (calls)
- [[backend.app.db.repositories.Repository.update_email_labels|update_email_labels]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)
- [[backend.app.mail.fingerprint.content_fingerprint|content_fingerprint]] (calls)
- `now` (`datetime.datetime.now`, calls-inferred)
- `AsyncClient` (`httpx.AsyncClient`, calls-inferred)

## Reads

- [[table_emails]]

## Writes

- [[table_accounts]]
- [[table_emails]]

## Side Effects

- async I/O; SQLite
