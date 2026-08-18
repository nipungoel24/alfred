---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.eligibility.MailEligibilityPolicy
qualified_name: backend.app.mail.eligibility.MailEligibilityPolicy.should_display_in_all_mail
source: backend/app/mail/eligibility.py
line: 204
status: active
tags: [gmail, function]
---

# should_display_in_all_mail

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

All Mail = received inbox, archived received, and sent messages.

## Location

`backend/app/mail/eligibility.py:204`

## Signature

```python
(label_ids: list[str] | set[str] | None) -> bool
```

## Parameters

- `label_ids` (`list[str] | set[str] | None`)

## Returns

`bool`

## Side Effects

- none statically observed
