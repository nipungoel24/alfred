---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.email_eligibility
source: backend/app/db/repositories.py
line: 102
status: active
tags: [database, function]
---

# email_eligibility

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Persisted eligibility projection for one message.

## Location

`backend/app/db/repositories.py:102`

## Signature

```python
(self, email_id: str) -> dict | None
```

## Parameters

- `self`
- `email_id` (`str`)

## Returns

`dict | None`

## Calls

- `loads` (`json.loads`, calls-inferred)

## Called By

- [[backend.tests.test_allmail.test_backfill_skips_cached_rows_and_updates_labels|test_backfill_skips_cached_rows_and_updates_labels]]
- [[backend.tests.test_eligibility.test_history_label_changes_refresh_via_metadata|test_history_label_changes_refresh_via_metadata]]
- [[backend.tests.test_eligibility.test_label_only_history_update_recomputes_state|test_label_only_history_update_recomputes_state]]
- [[backend.tests.test_eligibility.test_permanent_delete_marks_excluded_not_destroyed|test_permanent_delete_marks_excluded_not_destroyed]]

## Reads

- [[table_emails]]

## Side Effects

- SQLite
