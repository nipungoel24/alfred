---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.save_account
source: backend/app/db/repositories.py
line: 432
status: active
tags: [database, function]
---

# save_account

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `save_account` in `backend/app/db/repositories.py`.

## Location

`backend/app/db/repositories.py:432`

## Signature

```python
(self, account: EmailAccount)
```

## Parameters

- `self`
- `account` (`EmailAccount`)

## Calls

- `now` (`datetime.datetime.now`, calls-inferred)

## Called By

- [[backend.app.mail.providers.gmail.GmailProvider.backfill_messages|backfill_messages]]
- [[backend.app.mail.providers.gmail.GmailProvider.sync_messages|sync_messages]]
- [[backend.tests.test_allmail._account|_account]]
- [[backend.tests.test_eligibility.test_history_label_changes_refresh_via_metadata|test_history_label_changes_refresh_via_metadata]]
- [[backend.tests.test_eligibility.test_history_spam_arrival_is_never_cached|test_history_spam_arrival_is_never_cached]]
- [[backend.tests.test_task_migration.test_migration_idempotency_and_preservation|test_migration_idempotency_and_preservation]]

## Writes

- [[table_accounts]]

## Side Effects

- SQLite
