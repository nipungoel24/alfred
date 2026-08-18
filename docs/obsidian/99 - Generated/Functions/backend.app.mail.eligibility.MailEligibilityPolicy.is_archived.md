---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.eligibility.MailEligibilityPolicy
qualified_name: backend.app.mail.eligibility.MailEligibilityPolicy.is_archived
source: backend/app/mail/eligibility.py
line: 199
status: active
tags: [gmail, function]
---

# is_archived

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Archived received message (no INBOX, not sent/spam/trash/draft).

## Location

`backend/app/mail/eligibility.py:199`

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
