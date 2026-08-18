---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.eligibility.MailEligibilityPolicy
qualified_name: backend.app.mail.eligibility.MailEligibilityPolicy.is_unread
source: backend/app/mail/eligibility.py
line: 214
status: active
tags: [gmail, function]
---

# is_unread

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `is_unread` in `backend/app/mail/eligibility.py`.

## Location

`backend/app/mail/eligibility.py:214`

## Signature

```python
(label_ids: list[str] | set[str] | None) -> bool
```

## Parameters

- `label_ids` (`list[str] | set[str] | None`)

## Returns

`bool`

## Called By

- [[backend.app.main.analyze_all|analyze_all]]
- [[backend.app.main.sync_account|sync_account]]

## Side Effects

- none statically observed
