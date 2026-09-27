---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_task_reconcile_idempotency
qualified_name: backend.tests.test_task_reconcile_idempotency.store
source: backend/tests/test_task_reconcile_idempotency.py
line: 88
status: active
tags: [test, function]
---

# store

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Persist an email and its analysis the way the sync path does.

## Location

`backend/tests/test_task_reconcile_idempotency.py:88`

## Signature

```python
(repo, email: Email, analysis: EmailAnalysis)
```

## Parameters

- `repo`
- `email` (`Email`)
- `analysis` (`EmailAnalysis`)

## Calls

- [[backend.app.db.repositories.Repository.save_analysis|save_analysis]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)

## Writes

- [[table_email_analysis]]
- [[table_emails]]

## Side Effects

- SQLite
