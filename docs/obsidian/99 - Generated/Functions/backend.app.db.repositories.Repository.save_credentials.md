---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.save_credentials
source: backend/app/db/repositories.py
line: 478
status: active
tags: [database, function]
---

# save_credentials

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `save_credentials` in `backend/app/db/repositories.py`.

## Location

`backend/app/db/repositories.py:478`

## Signature

```python
(self, account_id: str, encrypted_refresh_token, encrypted_access_token, expires_at: str)
```

## Parameters

- `self`
- `account_id` (`str`)
- `encrypted_refresh_token`
- `encrypted_access_token`
- `expires_at` (`str`)

## Called By

- [[backend.app.mail.providers.gmail.GmailProvider._ensure_access_token|_ensure_access_token]]

## Writes

- [[table_credentials]]

## Side Effects

- SQLite
