---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_task_user_corrections
qualified_name: backend.tests.test_task_user_corrections.test_migration_service_never_revives_dismissed
source: backend/tests/test_task_user_corrections.py
line: 200
status: active
tags: [test, function, test]
---

# test_migration_service_never_revives_dismissed

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

derive -> dismiss -> TaskMigrationService -> no active task reappears,

## Location

`backend/tests/test_task_user_corrections.py:200`

## Signature

```python
(tmp_path)
```

## Parameters

- `tmp_path`

## Calls

- [[backend.app.db.repositories.Repository|Repository]] (calls)
- [[backend.app.schemas.Email|Email]] (calls)
- [[backend.app.schemas.EmailAnalysis|EmailAnalysis]] (calls)

## Side Effects

- none statically observed
