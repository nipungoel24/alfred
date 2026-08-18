---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.app.mail.eligibility
source: backend/app/mail/eligibility.py
status: active
tags: [module, backend]
---

# backend.app.mail.eligibility

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/app/mail/eligibility.py`

## Imports

- `Enum` ← `enum.Enum`
- `annotations` ← `__future__.annotations`

## Classes

- [[backend.app.mail.eligibility.BackfillState|BackfillState]]
- [[backend.app.mail.eligibility.GmailCategory|GmailCategory]]
- [[backend.app.mail.eligibility.MailEligibilityPolicy|MailEligibilityPolicy]]
- [[backend.app.mail.eligibility.MailboxState|MailboxState]]
- [[backend.app.mail.eligibility.PipelineEligibility|PipelineEligibility]]

## Functions

- [[backend.app.mail.eligibility.MailEligibilityPolicy.analysis_queue_priority|analysis_queue_priority]]
- [[backend.app.mail.eligibility.MailEligibilityPolicy.gmail_category|gmail_category]]
- [[backend.app.mail.eligibility.MailEligibilityPolicy.is_archived|is_archived]]
- [[backend.app.mail.eligibility.MailEligibilityPolicy.is_excluded|is_excluded]]
- [[backend.app.mail.eligibility.MailEligibilityPolicy.is_important_gmail|is_important_gmail]]
- [[backend.app.mail.eligibility.MailEligibilityPolicy.is_sent|is_sent]]
- [[backend.app.mail.eligibility.MailEligibilityPolicy.is_unread|is_unread]]
- [[backend.app.mail.eligibility.MailEligibilityPolicy.mailbox_state|mailbox_state]]
- [[backend.app.mail.eligibility.MailEligibilityPolicy.pipeline_eligibility|pipeline_eligibility]]
- [[backend.app.mail.eligibility.MailEligibilityPolicy.should_display_in_all_mail|should_display_in_all_mail]]
- [[backend.app.mail.eligibility.MailEligibilityPolicy.should_display_in_inbox|should_display_in_inbox]]
- [[backend.app.mail.eligibility.MailEligibilityPolicy.should_include_in_attention|should_include_in_attention]]
- [[backend.app.mail.eligibility.MailEligibilityPolicy.should_include_in_briefing|should_include_in_briefing]]
- [[backend.app.mail.eligibility.MailEligibilityPolicy.should_schedule_analysis|should_schedule_analysis]]
- [[backend.app.mail.eligibility.gmail_category_from_labels|gmail_category_from_labels]]
- [[backend.app.mail.eligibility.mailbox_state_from_labels|mailbox_state_from_labels]]

## Constants

- `ALL_MAIL_STATES`
- `CATEGORY_LABEL_TO_UI`
- `LABEL_CATEGORY_FORUMS`
- `LABEL_CATEGORY_PERSONAL`
- `LABEL_CATEGORY_PROMOTIONS`
- `LABEL_CATEGORY_SOCIAL`
- `LABEL_CATEGORY_UPDATES`
- `LABEL_DRAFT`
- `LABEL_IMPORTANT`
- `LABEL_INBOX`
- `LABEL_SENT`
- `LABEL_SPAM`
- `LABEL_STARRED`
- `LABEL_TRASH`
- `LABEL_UNREAD`
- `LAZY_CATEGORIES`
- `SYSTEM_LABELS`
