---
type: database-table
generated: true
layer: database
qualified_name: table_email_analysis
source: backend/app/db/database.py
status: active
tags: [database, database-table]
---

# email_analysis

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

SQLite table `email_analysis` defined in the Alfred schema.

## Columns

- `email_id` · PRIMARY KEY
- `content_hash`
- `model_name`
- `schema_version`
- `payload`
- `analyzed_at`

## Ownership

See [[Data Ownership]] for source/derived/user-state classification.
