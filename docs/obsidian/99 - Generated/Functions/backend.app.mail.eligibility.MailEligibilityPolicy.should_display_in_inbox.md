---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.eligibility.MailEligibilityPolicy
qualified_name: backend.app.mail.eligibility.MailEligibilityPolicy.should_display_in_inbox
source: backend/app/mail/eligibility.py
line: 161
status: active
tags: [gmail, function]
---

# should_display_in_inbox

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Alfred's current Inbox shows active Gmail Inbox messages only.

## Location

`backend/app/mail/eligibility.py:161`

## Signature

```python
(label_ids: list[str] | set[str] | None) -> bool
```

## Parameters

- `label_ids` (`list[str] | set[str] | None`)

## Returns

`bool`

## Called By

- [[backend.tests.test_eligibility.test_inbox_primary|test_inbox_primary]]
- [[backend.tests.test_eligibility.test_spam_state|test_spam_state]]

## Side Effects

- none statically observed
