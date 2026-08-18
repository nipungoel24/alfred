---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.eligibility.MailEligibilityPolicy
qualified_name: backend.app.mail.eligibility.MailEligibilityPolicy.should_schedule_analysis
source: backend/app/mail/eligibility.py
line: 279
status: active
tags: [gmail, function]
---

# should_schedule_analysis

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Whether a message should be enqueued for background analysis.

## Location

`backend/app/mail/eligibility.py:279`

## Signature

```python
(cls, label_ids: list[str] | set[str] | None, user_requested: bool = False) -> bool
```

## Parameters

- `cls`
- `label_ids` (`list[str] | set[str] | None`)
- `user_requested` (`bool`)

## Returns

`bool`

## Called By

- [[backend.app.main.analyze_all|analyze_all]]
- [[backend.app.main.sync_account|sync_account]]
- [[backend.tests.test_allmail.test_archived_excluded_from_intelligence|test_archived_excluded_from_intelligence]]
- [[backend.tests.test_allmail.test_sent_visible_but_excluded_from_intelligence|test_sent_visible_but_excluded_from_intelligence]]
- [[backend.tests.test_eligibility.test_lazy_categories_not_scheduled_by_default|test_lazy_categories_not_scheduled_by_default]]
- [[backend.tests.test_eligibility.test_updates_with_required_action_eligible_for_semantic_analysis|test_updates_with_required_action_eligible_for_semantic_analysis]]

## Side Effects

- none statically observed
