---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.email
source: backend/app/db/repositories.py
line: 93
status: active
tags: [database, function]
---

# email

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `email` in `backend/app/db/repositories.py`.

## Location

`backend/app/db/repositories.py:93`

## Signature

```python
(self, email_id: str)
```

## Parameters

- `self`
- `email_id` (`str`)

## Calls

- `model_validate_json` (`backend.app.schemas.Email.model_validate_json`, calls-inferred)

## Called By

- [[backend.app.mail.providers.gmail.GmailProvider.sync_messages|sync_messages]]
- [[backend.tests.test_allmail.test_backfill_first_page_and_resume|test_backfill_first_page_and_resume]]
- [[backend.tests.test_eligibility.test_history_label_changes_refresh_via_metadata|test_history_label_changes_refresh_via_metadata]]
- [[backend.tests.test_eligibility.test_history_spam_arrival_is_never_cached|test_history_spam_arrival_is_never_cached]]
- [[backend.tests.test_eligibility.test_label_only_history_update_recomputes_state|test_label_only_history_update_recomputes_state]]
- [[backend.tests.test_eligibility.test_permanent_delete_marks_excluded_not_destroyed|test_permanent_delete_marks_excluded_not_destroyed]]

## Reads

- [[table_emails]]

## Side Effects

- SQLite
