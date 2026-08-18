---
type: database-table
generated: true
layer: database
qualified_name: table_emails
source: backend/app/db/database.py
status: active
tags: [database, database-table]
---

# emails

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

SQLite table `emails` defined in the Alfred schema.

## Columns

- `id` · PRIMARY KEY
- `payload`
- `content_hash`
- `imported_at`
- `account_id`
- `thread_id`
- `sender_col`
- `subject_col`
- `received_at_col`
- `label_ids_json`
- `mailbox_state`
- `gmail_category`
- `pipeline_eligibility`

## Ownership

See [[Data Ownership]] for source/derived/user-state classification.
