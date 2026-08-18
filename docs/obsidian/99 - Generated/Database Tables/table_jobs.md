---
type: database-table
generated: true
layer: database
qualified_name: table_jobs
source: backend/app/db/database.py
status: active
tags: [database, database-table]
---

# jobs

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

SQLite table `jobs` defined in the Alfred schema.

## Columns

- `id` · PRIMARY KEY
- `job_type`
- `target_id`
- `priority`
- `status`
- `attempts`
- `max_attempts`
- `created_at`
- `started_at`
- `completed_at`
- `error_code`
- `error_message`
- `not_before`

## Ownership

See [[Data Ownership]] for source/derived/user-state classification.
