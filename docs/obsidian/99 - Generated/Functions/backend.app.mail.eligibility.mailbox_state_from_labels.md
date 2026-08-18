---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.eligibility
qualified_name: backend.app.mail.eligibility.mailbox_state_from_labels
source: backend/app/mail/eligibility.py
line: 122
status: active
tags: [gmail, function]
---

# mailbox_state_from_labels

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Derive the explicit mailbox state from Gmail label IDs.

## Location

`backend/app/mail/eligibility.py:122`

## Signature

```python
(label_ids: list[str] | set[str] | None) -> MailboxState
```

## Parameters

- `label_ids` (`list[str] | set[str] | None`)

## Returns

`MailboxState`

## Called By

- [[backend.app.db.repositories.Repository.update_email_labels|update_email_labels]]
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]]
- [[backend.tests.test_eligibility.test_archived_state|test_archived_state]]
- [[backend.tests.test_eligibility.test_inbox_primary|test_inbox_primary]]
- [[backend.tests.test_eligibility.test_inbox_promotions|test_inbox_promotions]]
- [[backend.tests.test_eligibility.test_spam_state|test_spam_state]]
- [[backend.tests.test_eligibility.test_spam_wins_over_inbox|test_spam_wins_over_inbox]]
- [[backend.tests.test_eligibility.test_trash_state|test_trash_state]]

## Side Effects

- none statically observed
