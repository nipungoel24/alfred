---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.email_counts
source: backend/app/db/repositories.py
line: 247
status: active
tags: [database, function]
---

# email_counts

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Scope + category counts derived from stored Gmail labels.

## Location

`backend/app/db/repositories.py:247`

## Signature

```python
(self, account_id: str | None = None) -> dict
```

## Parameters

- `self`
- `account_id` (`str | None`)

## Returns

`dict`

## Called By

- [[backend.tests.test_allmail.test_backfill_first_page_and_resume|test_backfill_first_page_and_resume]]
- [[backend.tests.test_allmail.test_backfill_skips_cached_rows_and_updates_labels|test_backfill_skips_cached_rows_and_updates_labels]]
- [[backend.tests.test_allmail.test_counts_report_inbox_allmail_excluded|test_counts_report_inbox_allmail_excluded]]
- [[backend.tests.test_eligibility.test_category_counts_derive_from_labels|test_category_counts_derive_from_labels]]
- [[backend.tests.test_eligibility.test_spam_transition_hides_from_projections|test_spam_transition_hides_from_projections]]

## Reads

- [[table_emails]]

## Side Effects

- SQLite
