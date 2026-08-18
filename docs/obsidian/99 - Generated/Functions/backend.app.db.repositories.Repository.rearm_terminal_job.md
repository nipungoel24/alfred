---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.rearm_terminal_job
source: backend/app/db/repositories.py
line: 665
status: active
tags: [database, function]
---

# rearm_terminal_job

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Re-arm a job row that finished or paused, when work remains.

## Location

`backend/app/db/repositories.py:665`

## Signature

```python
(self, job_id: str)
```

## Parameters

- `self`
- `job_id` (`str`)

## Called By

- [[backend.tests.test_backfill_jobs.test_rearm_does_not_touch_backoff_retries|test_rearm_does_not_touch_backoff_retries]]
- [[backend.tests.test_backfill_jobs.test_rearm_terminal_job_for_resume|test_rearm_terminal_job_for_resume]]

## Writes

- [[table_jobs]]

## Side Effects

- SQLite
