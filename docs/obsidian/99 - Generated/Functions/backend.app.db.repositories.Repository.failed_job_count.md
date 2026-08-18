---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.failed_job_count
source: backend/app/db/repositories.py
line: 730
status: active
tags: [database, function]
---

# failed_job_count

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `failed_job_count` in `backend/app/db/repositories.py`.

## Location

`backend/app/db/repositories.py:730`

## Signature

```python
(self, job_type: str = None) -> int
```

## Parameters

- `self`
- `job_type` (`str`)

## Returns

`int`

## Reads

- [[table_jobs]]

## Side Effects

- SQLite
