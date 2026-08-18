---
type: database-table
generated: true
layer: database
qualified_name: table_tasks
source: backend/app/db/database.py
status: active
tags: [database, database-table]
---

# tasks

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

SQLite table `tasks` defined in the Alfred schema.

## Columns

- `id` · PRIMARY KEY
- `source_thread_id`
- `title`
- `description`
- `due_at`
- `priority`
- `status`
- `created_at`
- `derivation_version`
- `confidence`
- `fingerprint`

## Ownership

See [[Data Ownership]] for source/derived/user-state classification.
