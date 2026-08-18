---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.all_analyses_with_emails
source: backend/app/db/repositories.py
line: 391
status: active
tags: [database, function]
---

# all_analyses_with_emails

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Load all email+analysis pairs efficiently in a single query.

## Location

`backend/app/db/repositories.py:391`

## Signature

```python
(self, model: str, schema = '1') -> list[tuple[Email, EmailAnalysis]]
```

## Parameters

- `self`
- `model` (`str`)
- `schema`

## Returns

`list[tuple[Email, EmailAnalysis]]`

## Calls

- `model_validate_json` (`backend.app.schemas.Email.model_validate_json`, calls-inferred)
- `model_validate_json` (`backend.app.schemas.EmailAnalysis.model_validate_json`, calls-inferred)

## Called By

- [[backend.app.services.task_derivation.rebuild_tasks_from_analyses|rebuild_tasks_from_analyses]]

## Reads

- [[table_email_analysis]]
- [[table_emails]]

## Side Effects

- SQLite
