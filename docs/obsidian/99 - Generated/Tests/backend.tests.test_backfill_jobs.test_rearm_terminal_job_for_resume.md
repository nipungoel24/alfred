---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_backfill_jobs
qualified_name: backend.tests.test_backfill_jobs.test_rearm_terminal_job_for_resume
source: backend/tests/test_backfill_jobs.py
line: 113
status: active
tags: [test, function, test]
---

# test_rearm_terminal_job_for_resume

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_rearm_terminal_job_for_resume` in `backend/tests/test_backfill_jobs.py`.

## Location

`backend/tests/test_backfill_jobs.py:113`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.enqueue_job|enqueue_job]] (calls)
- [[backend.app.db.repositories.Repository.job|job]] (calls)
- [[backend.app.db.repositories.Repository.rearm_terminal_job|rearm_terminal_job]] (calls)
- [[backend.app.db.repositories.Repository.update_job_status|update_job_status]] (calls)

## Reads

- [[table_jobs]]

## Writes

- [[table_jobs]]

## Side Effects

- SQLite
