---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main._briefing_eligible_emails
source: backend/app/main.py
line: 971
status: active
tags: [backend, function]
---

# _briefing_eligible_emails

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

One authoritative briefing candidate set: active inbox, not spam/

## Location

`backend/app/main.py:971`

## Signature

```python
() -> list[Email]
```

## Returns

`list[Email]`

## Calls

- [[backend.app.mail.eligibility.MailEligibilityPolicy.should_include_in_briefing|should_include_in_briefing]] (calls)
- [[backend.app.mail.fingerprint.content_fingerprint|content_fingerprint]] (calls)

## Side Effects

- none statically observed
