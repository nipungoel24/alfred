---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.update_email_labels
source: backend/app/db/repositories.py
line: 128
status: active
tags: [database, function]
---

# update_email_labels

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Recompute mailbox state / category / eligibility for a message.

## Location

`backend/app/db/repositories.py:128`

## Signature

```python
(self, email_id: str, label_ids: list[str]) -> bool
```

## Parameters

- `self`
- `email_id` (`str`)
- `label_ids` (`list[str]`)

## Returns

`bool`

## Calls

- `model_dump_json` (`backend.app.db.repositories.Repository.email.model_dump_json`, calls-inferred)
- [[backend.app.mail.eligibility.MailEligibilityPolicy.pipeline_eligibility|pipeline_eligibility]] (calls)
- [[backend.app.mail.eligibility.gmail_category_from_labels|gmail_category_from_labels]] (calls)
- [[backend.app.mail.eligibility.mailbox_state_from_labels|mailbox_state_from_labels]] (calls)
- `model_validate_json` (`backend.app.schemas.Email.model_validate_json`, calls-inferred)
- `dumps` (`json.dumps`, calls-inferred)

## Called By

- [[backend.app.mail.providers.gmail.GmailProvider.backfill_messages|backfill_messages]]
- [[backend.app.mail.providers.gmail.GmailProvider.sync_messages|sync_messages]]
- [[backend.tests.test_eligibility.test_label_only_history_update_recomputes_state|test_label_only_history_update_recomputes_state]]
- [[backend.tests.test_eligibility.test_spam_transition_hides_from_projections|test_spam_transition_hides_from_projections]]

## Reads

- [[table_emails]]

## Writes

- [[table_emails]]

## Side Effects

- SQLite
