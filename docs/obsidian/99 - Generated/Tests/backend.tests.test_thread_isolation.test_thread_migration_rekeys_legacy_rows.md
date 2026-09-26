---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_thread_isolation
qualified_name: backend.tests.test_thread_isolation.test_thread_migration_rekeys_legacy_rows
source: backend/tests/test_thread_isolation.py
line: 147
status: active
tags: [test, function, test]
---

# test_thread_migration_rekeys_legacy_rows

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Legacy (raw thread id) rows migrate to scoped threads with tasks.

## Location

`backend/tests/test_thread_isolation.py:147`

## Signature

```python
(tmp_path: Path)
```

## Parameters

- `tmp_path` (`Path`)

## Calls

- [[backend.app.db.repositories.Repository|Repository]] (calls)
- [[backend.app.mail.identity.scoped_thread_id|scoped_thread_id]] (calls)
- [[backend.app.schemas.Email|Email]] (calls)

## Reads

- [[table_emails]]

## Writes

- [[table_emails]]
- [[table_tasks]]

## Side Effects

- SQLite
