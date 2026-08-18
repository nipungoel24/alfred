---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.reset_retryable_jobs
source: backend/app/db/repositories.py
line: 739
status: active
tags: [database, function]
---

# reset_retryable_jobs

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Reset retryable_failed jobs back to queued if under max_attempts.

## Location

`backend/app/db/repositories.py:739`

## Signature

```python
(self)
```

## Parameters

- `self`

## Writes

- [[table_jobs]]

## Side Effects

- SQLite
