---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_eligibility
qualified_name: backend.tests.test_eligibility.test_mixed_label_thread_keeps_active_messages_visible
source: backend/tests/test_eligibility.py
line: 319
status: active
tags: [test, function, test]
---

# test_mixed_label_thread_keeps_active_messages_visible

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_mixed_label_thread_keeps_active_messages_visible` in `backend/tests/test_eligibility.py`.

## Location

`backend/tests/test_eligibility.py:319`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- `commit` (`backend.app.db.repositories.Repository.con.commit`, calls-inferred)
- `execute` (`backend.app.db.repositories.Repository.con.execute`, calls-inferred)
- [[backend.app.db.repositories.Repository.emails_by_thread|emails_by_thread]] (calls)
- [[backend.app.db.repositories.Repository.emails_filtered|emails_filtered]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)

## Reads

- [[table_emails]]

## Writes

- [[table_emails]]

## Side Effects

- SQLite
