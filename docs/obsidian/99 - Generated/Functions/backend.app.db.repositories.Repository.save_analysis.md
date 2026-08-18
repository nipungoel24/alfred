---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.save_analysis
source: backend/app/db/repositories.py
line: 380
status: active
tags: [database, function]
---

# save_analysis

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Save analysis result. Does NOT create tasks — that is TaskDerivationService's job.

## Location

`backend/app/db/repositories.py:380`

## Signature

```python
(self, email_id: str, fingerprint: str, model: str, analysis: EmailAnalysis, schema = '1')
```

## Parameters

- `self`
- `email_id` (`str`)
- `fingerprint` (`str`)
- `model` (`str`)
- `analysis` (`EmailAnalysis`)
- `schema`

## Calls

- `now` (`datetime.datetime.now`, calls-inferred)

## Called By

- [[backend.tests.test_task_migration.test_migration_idempotency_and_preservation|test_migration_idempotency_and_preservation]]
- [[backend.tests.test_task_migration.test_migration_rollback|test_migration_rollback]]

## Writes

- [[table_email_analysis]]

## Side Effects

- SQLite
