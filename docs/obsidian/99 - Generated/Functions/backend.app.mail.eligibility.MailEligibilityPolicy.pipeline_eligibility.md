---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.eligibility.MailEligibilityPolicy
qualified_name: backend.app.mail.eligibility.MailEligibilityPolicy.pipeline_eligibility
source: backend/app/mail/eligibility.py
line: 168
status: active
tags: [gmail, function]
---

# pipeline_eligibility

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

ACTIVE / DEFERRED / EXCLUDED for the intelligence pipeline.

## Location

`backend/app/mail/eligibility.py:168`

## Signature

```python
(label_ids: list[str] | set[str] | None) -> PipelineEligibility
```

## Parameters

- `label_ids` (`list[str] | set[str] | None`)

## Returns

`PipelineEligibility`

## Called By

- [[backend.app.db.repositories.Repository.update_email_labels|update_email_labels]]
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]]
- [[backend.tests.test_allmail.test_sent_visible_but_excluded_from_intelligence|test_sent_visible_but_excluded_from_intelligence]]
- [[backend.tests.test_eligibility.test_archive_to_inbox_restores|test_archive_to_inbox_restores]]
- [[backend.tests.test_eligibility.test_inbox_to_archive_excludes|test_inbox_to_archive_excludes]]
- [[backend.tests.test_eligibility.test_inbox_to_spam_excludes|test_inbox_to_spam_excludes]]
- [[backend.tests.test_eligibility.test_sent_and_draft_are_excluded|test_sent_and_draft_are_excluded]]
- [[backend.tests.test_eligibility.test_spam_to_inbox_restores_eligibility|test_spam_to_inbox_restores_eligibility]]
- [[backend.tests.test_eligibility.test_updates_with_required_action_eligible_for_semantic_analysis|test_updates_with_required_action_eligible_for_semantic_analysis]]

## Side Effects

- none statically observed
