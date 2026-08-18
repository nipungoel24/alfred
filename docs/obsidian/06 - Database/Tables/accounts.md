---
type: database-table
layer: database
status: active
source: backend/app/db/database.py
tags:
  - database
---

# accounts

Connected email providers. One row per provider account (`gmail_<email>`).

## Data classification

**User state** — includes the sync cursor JSON (`history_id`, `next_page_token`, typed backfill state).

## Columns

See generated schema note: [[table_accounts]].

## Written By

- [[GET --api-accounts-gmail-callback|gmail_callback]] (account creation on OAuth)
- [[backend.app.mail.providers.gmail.GmailProvider.sync_messages]]
- [[backend.app.mail.providers.gmail.GmailProvider.backfill_messages]]
- [[backend.app.db.repositories.Repository.save_account]]

## Read By

- [[GET --api-accounts]]
- [[backend.app.main.lifespan]] (backfill resume)
- [[POST --api-accounts-{account_id}-sync|sync_account]] / [[backend.app.main.backfill_account]]

## Sync cursor contract

`sync_cursor` is JSON: `history_id` (Gmail incremental cursor), `next_page_token` (inbox pagination), `backfill_state` + `backfill_page_token` + counters + `backfill_estimate` ([[backend.app.mail.backfill]]).

## Related

- [[credentials]]
- [[Gmail Incremental Sync Flow]]
- [[All Mail Backfill Flow]]
