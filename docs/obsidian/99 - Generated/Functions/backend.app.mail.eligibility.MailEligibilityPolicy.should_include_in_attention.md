---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.eligibility.MailEligibilityPolicy
qualified_name: backend.app.mail.eligibility.MailEligibilityPolicy.should_include_in_attention
source: backend/app/mail/eligibility.py
line: 242
status: active
tags: [gmail, function]
---

# should_include_in_attention

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Important/Needs-Reply attention projections require active inbox.

## Location

`backend/app/mail/eligibility.py:242`

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
