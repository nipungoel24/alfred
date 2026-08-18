---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.next_job
source: backend/app/db/repositories.py
line: 626
status: active
tags: [database, function, critical-path]
---

# next_job

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Get the next queued job by priority, honouring not_before.

## Location

`backend/app/db/repositories.py:626`

## Signature

```python
(self, job_type: str = None, now_iso: str | None = None)
```

## Parameters

- `self`
- `job_type` (`str`)
- `now_iso` (`str | None`)

## Calls

- `now` (`datetime.datetime.now`, calls-inferred)

## Called By

- [[backend.tests.test_backfill_jobs.test_backfill_priority_is_below_analysis|test_backfill_priority_is_below_analysis]]
- [[backend.tests.test_backfill_jobs.test_backoff_and_promotion_cycle|test_backoff_and_promotion_cycle]]
- [[backend.tests.test_backfill_jobs.test_next_job_honours_not_before|test_next_job_honours_not_before]]

## Reads

- [[table_jobs]]

## Side Effects

- SQLite
