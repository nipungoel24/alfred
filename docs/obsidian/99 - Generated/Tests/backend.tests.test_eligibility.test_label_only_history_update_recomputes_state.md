---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_eligibility
qualified_name: backend.tests.test_eligibility.test_label_only_history_update_recomputes_state
source: backend/tests/test_eligibility.py
line: 199
status: active
tags: [test, function, test]
---

# test_label_only_history_update_recomputes_state

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_label_only_history_update_recomputes_state` in `backend/tests/test_eligibility.py`.

## Location

`backend/tests/test_eligibility.py:199`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.email|email]] (calls)
- [[backend.app.db.repositories.Repository.email_eligibility|email_eligibility]] (calls)
- [[backend.app.db.repositories.Repository.update_email_labels|update_email_labels]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)

## Reads

- [[table_emails]]

## Writes

- [[table_emails]]

## Side Effects

- SQLite
