---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.pending_job_count
source: backend/app/db/repositories.py
line: 712
status: active
tags: [database, function]
---

# pending_job_count

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `pending_job_count` in `backend/app/db/repositories.py`.

## Location

`backend/app/db/repositories.py:712`

## Signature

```python
(self, job_type: str = None) -> int
```

## Parameters

- `self`
- `job_type` (`str`)

## Returns

`int`

## Called By

- [[backend.tests.test_backfill_jobs.test_backfill_job_is_single_durable_row|test_backfill_job_is_single_durable_row]]

## Reads

- [[table_jobs]]

## Side Effects

- SQLite
