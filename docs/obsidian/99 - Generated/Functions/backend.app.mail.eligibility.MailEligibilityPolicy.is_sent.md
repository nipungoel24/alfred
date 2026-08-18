---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.eligibility.MailEligibilityPolicy
qualified_name: backend.app.mail.eligibility.MailEligibilityPolicy.is_sent
source: backend/app/mail/eligibility.py
line: 193
status: active
tags: [gmail, function]
---

# is_sent

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Sent-only message (SENT label, no INBOX).

## Location

`backend/app/mail/eligibility.py:193`

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
