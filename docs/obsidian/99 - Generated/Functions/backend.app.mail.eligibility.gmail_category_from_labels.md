---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.eligibility
qualified_name: backend.app.mail.eligibility.gmail_category_from_labels
source: backend/app/mail/eligibility.py
line: 108
status: active
tags: [gmail, function]
---

# gmail_category_from_labels

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Map Gmail CATEGORY_* labels onto the Alfred UI category.

## Location

`backend/app/mail/eligibility.py:108`

## Signature

```python
(label_ids: list[str] | set[str] | None) -> GmailCategory
```

## Parameters

- `label_ids` (`list[str] | set[str] | None`)

## Returns

`GmailCategory`

## Called By

- [[backend.app.db.repositories.Repository.update_email_labels|update_email_labels]]
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]]
- [[backend.tests.test_eligibility.test_inbox_forums|test_inbox_forums]]
- [[backend.tests.test_eligibility.test_inbox_primary|test_inbox_primary]]
- [[backend.tests.test_eligibility.test_inbox_promotions|test_inbox_promotions]]
- [[backend.tests.test_eligibility.test_inbox_social|test_inbox_social]]
- [[backend.tests.test_eligibility.test_inbox_updates|test_inbox_updates]]
- [[backend.tests.test_eligibility.test_inbox_without_category_is_primary|test_inbox_without_category_is_primary]]

## Side Effects

- none statically observed
