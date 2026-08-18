---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.providers.gmail.GmailProvider
qualified_name: backend.app.mail.providers.gmail.GmailProvider._ensure_access_token
source: backend/app/mail/providers/gmail.py
line: 88
status: active
tags: [gmail, function]
---

# _ensure_access_token

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Return a valid access token, refreshing via the refresh token when

## Location

`backend/app/mail/providers/gmail.py:88`

## Signature

```python
(self, account, credentials: Dict[str, Any], repo) -> str
```

## Parameters

- `self`
- `account`
- `credentials` (`Dict[str, Any]`)
- `repo`

## Returns

`str`

## Calls

- [[backend.app.db.repositories.Repository.save_credentials|save_credentials]] (calls)
- `fromisoformat` (`datetime.datetime.fromisoformat`, calls-inferred)
- `now` (`datetime.datetime.now`, calls-inferred)
- `timedelta` (`datetime.timedelta`, calls-inferred)

## Writes

- [[table_credentials]]

## Side Effects

- async I/O; SQLite; handles credentials/tokens — see [[Token Security]]
