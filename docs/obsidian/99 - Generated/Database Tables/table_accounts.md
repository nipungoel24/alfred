---
type: database-table
generated: true
layer: database
qualified_name: table_accounts
source: backend/app/db/database.py
status: active
tags: [database, database-table]
---

# accounts

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

SQLite table `accounts` defined in the Alfred schema.

## Columns

- `id` · PRIMARY KEY
- `provider`
- `email_address`
- `display_name`
- `connection_status`
- `last_sync_at`
- `sync_cursor`
- `created_at`
- `updated_at`

## Ownership

See [[Data Ownership]] for source/derived/user-state classification.
