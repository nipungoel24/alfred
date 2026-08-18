---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.eligibility.MailEligibilityPolicy
qualified_name: backend.app.mail.eligibility.MailEligibilityPolicy.should_include_in_briefing
source: backend/app/mail/eligibility.py
line: 220
status: active
tags: [gmail, function]
---

# should_include_in_briefing

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Default briefing candidates: active inbox, not spam/trash/draft/

## Location

`backend/app/mail/eligibility.py:220`

## Signature

```python
(label_ids: list[str] | set[str] | None, analysis_priority: str | None = None, needs_reply: bool | None = None) -> bool
```

## Parameters

- `label_ids` (`list[str] | set[str] | None`)
- `analysis_priority` (`str | None`)
- `needs_reply` (`bool | None`)

## Returns

`bool`

## Called By

- [[backend.app.main._briefing_eligible_emails|_briefing_eligible_emails]]
- [[backend.tests.test_allmail.test_archived_excluded_from_intelligence|test_archived_excluded_from_intelligence]]
- [[backend.tests.test_allmail.test_sent_visible_but_excluded_from_intelligence|test_sent_visible_but_excluded_from_intelligence]]
- [[backend.tests.test_eligibility.test_briefing_excludes_spam_trash_archived|test_briefing_excludes_spam_trash_archived]]
- [[backend.tests.test_eligibility.test_briefing_promotions_with_strong_signal_included|test_briefing_promotions_with_strong_signal_included]]
- [[backend.tests.test_eligibility.test_briefing_promotions_without_signal_excluded|test_briefing_promotions_without_signal_excluded]]

## Side Effects

- none statically observed
