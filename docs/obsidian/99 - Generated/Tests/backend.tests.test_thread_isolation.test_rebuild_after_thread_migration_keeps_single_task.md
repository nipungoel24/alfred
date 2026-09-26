---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_thread_isolation
qualified_name: backend.tests.test_thread_isolation.test_rebuild_after_thread_migration_keeps_single_task
source: backend/tests/test_thread_isolation.py
line: 220
status: active
tags: [test, function, test]
---

# test_rebuild_after_thread_migration_keeps_single_task

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Legacy v2 task (raw-thread fp) -> migrate -> rebuild -> one task.

## Location

`backend/tests/test_thread_isolation.py:220`

## Signature

```python
(tmp_path)
```

## Parameters

- `tmp_path`

## Calls

- [[backend.app.db.repositories.Repository|Repository]] (calls)
- [[backend.app.mail.identity.scoped_email_id|scoped_email_id]] (calls)
- [[backend.app.mail.identity.scoped_thread_id|scoped_thread_id]] (calls)
- [[backend.app.schemas.Email|Email]] (calls)
- [[backend.app.services.task_derivation._normalize_action|_normalize_action]] (calls)
- [[backend.app.services.task_derivation.task_fingerprint|task_fingerprint]] (calls)

## Writes

- [[table_email_analysis]]
- [[table_emails]]
- [[table_tasks]]

## Side Effects

- SQLite
