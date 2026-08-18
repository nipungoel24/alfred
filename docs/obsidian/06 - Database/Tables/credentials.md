---
type: database-table
layer: database
status: active
source: backend/app/db/database.py
tags:
  - database
  - security
---

# credentials

OAuth token storage. 1:1 with [[accounts]] (PK = account_id, FK cascade).

## Data classification

**Secrets** — `encrypted_refresh_token` and `encrypted_access_token` are DPAPI ciphertext (BLOBs); `expires_at` is the access-token expiry. Plaintext never touches this table.

## Written By

- [[GET --api-accounts-gmail-callback|gmail_callback]] (initial save)
- [[backend.app.mail.providers.gmail.GmailProvider._ensure_access_token]] (refresh rotation)

## Read By

- [[POST --api-accounts-{account_id}-sync|sync_account]] / [[backend.app.main.backfill_account]] (decrypt → call Gmail)
- [[backend.app.main._label_backfill]]

## Privacy notes

DPAPI protects against file-copy theft by other processes on the same machine/user boundary; it is not E2E encryption. See [[DPAPI]] and [[Token Security]].

## Related

- [[accounts]]
- [[Gmail OAuth Flow]]
- [[backend.app.db.secure_store]]
