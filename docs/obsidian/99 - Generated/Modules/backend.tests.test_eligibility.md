---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_eligibility
source: backend/tests/test_eligibility.py
status: active
tags: [module, backend]
---

# backend.tests.test_eligibility

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_eligibility.py`

## Imports

- `AsyncMock` ← `unittest.mock.AsyncMock`
- `Email` ← `backend.app.schemas.Email`
- `GmailCategory` ← `backend.app.mail.eligibility.GmailCategory`
- `LABEL_CATEGORY_FORUMS` ← `backend.app.mail.eligibility.LABEL_CATEGORY_FORUMS`
- `LABEL_CATEGORY_PERSONAL` ← `backend.app.mail.eligibility.LABEL_CATEGORY_PERSONAL`
- `LABEL_CATEGORY_PROMOTIONS` ← `backend.app.mail.eligibility.LABEL_CATEGORY_PROMOTIONS`
- `LABEL_CATEGORY_SOCIAL` ← `backend.app.mail.eligibility.LABEL_CATEGORY_SOCIAL`
- `LABEL_CATEGORY_UPDATES` ← `backend.app.mail.eligibility.LABEL_CATEGORY_UPDATES`
- `LABEL_DRAFT` ← `backend.app.mail.eligibility.LABEL_DRAFT`
- `LABEL_IMPORTANT` ← `backend.app.mail.eligibility.LABEL_IMPORTANT`
- `LABEL_INBOX` ← `backend.app.mail.eligibility.LABEL_INBOX`
- `LABEL_SENT` ← `backend.app.mail.eligibility.LABEL_SENT`
- `LABEL_SPAM` ← `backend.app.mail.eligibility.LABEL_SPAM`
- `LABEL_TRASH` ← `backend.app.mail.eligibility.LABEL_TRASH`
- `LABEL_UNREAD` ← `backend.app.mail.eligibility.LABEL_UNREAD`
- `MagicMock` ← `unittest.mock.MagicMock`
- `MailEligibilityPolicy` ← `backend.app.mail.eligibility.MailEligibilityPolicy`
- `MailboxState` ← `backend.app.mail.eligibility.MailboxState`
- `PipelineEligibility` ← `backend.app.mail.eligibility.PipelineEligibility`
- `Repository` ← `backend.app.db.repositories.Repository`
- `asyncio` ← `asyncio`
- `datetime` ← `datetime.datetime`
- `gmail_category_from_labels` ← `backend.app.mail.eligibility.gmail_category_from_labels`
- `json` ← `json`
- `mailbox_state_from_labels` ← `backend.app.mail.eligibility.mailbox_state_from_labels`
- `patch` ← `unittest.mock.patch`
- `pytest` ← `pytest`
- `timedelta` ← `datetime.timedelta`
- `timezone` ← `datetime.timezone`

## Functions

- [[backend.tests.test_eligibility._email|_email]]
- [[backend.tests.test_eligibility.repo|repo]]

## Tests

- [[backend.tests.test_eligibility.test_active_tasks_exclude_spam_sourced|test_active_tasks_exclude_spam_sourced]]
- [[backend.tests.test_eligibility.test_archive_to_inbox_restores|test_archive_to_inbox_restores]]
- [[backend.tests.test_eligibility.test_archived_state|test_archived_state]]
- [[backend.tests.test_eligibility.test_briefing_excludes_spam_trash_archived|test_briefing_excludes_spam_trash_archived]]
- [[backend.tests.test_eligibility.test_briefing_promotions_with_strong_signal_included|test_briefing_promotions_with_strong_signal_included]]
- [[backend.tests.test_eligibility.test_briefing_promotions_without_signal_excluded|test_briefing_promotions_without_signal_excluded]]
- [[backend.tests.test_eligibility.test_category_counts_derive_from_labels|test_category_counts_derive_from_labels]]
- [[backend.tests.test_eligibility.test_category_filter_is_db_driven|test_category_filter_is_db_driven]]
- [[backend.tests.test_eligibility.test_email_api_excluded_mail_never_listed|test_email_api_excluded_mail_never_listed]]
- [[backend.tests.test_eligibility.test_gmail_important_is_p0|test_gmail_important_is_p0]]
- [[backend.tests.test_eligibility.test_history_label_changes_refresh_via_metadata|test_history_label_changes_refresh_via_metadata]]
- [[backend.tests.test_eligibility.test_history_spam_arrival_is_never_cached|test_history_spam_arrival_is_never_cached]]
- [[backend.tests.test_eligibility.test_inbox_forums|test_inbox_forums]]
- [[backend.tests.test_eligibility.test_inbox_primary|test_inbox_primary]]
- [[backend.tests.test_eligibility.test_inbox_promotions|test_inbox_promotions]]
- [[backend.tests.test_eligibility.test_inbox_social|test_inbox_social]]
- [[backend.tests.test_eligibility.test_inbox_to_archive_excludes|test_inbox_to_archive_excludes]]
- [[backend.tests.test_eligibility.test_inbox_to_spam_excludes|test_inbox_to_spam_excludes]]
- [[backend.tests.test_eligibility.test_inbox_updates|test_inbox_updates]]
- [[backend.tests.test_eligibility.test_inbox_without_category_is_primary|test_inbox_without_category_is_primary]]
- [[backend.tests.test_eligibility.test_label_only_history_update_recomputes_state|test_label_only_history_update_recomputes_state]]
- [[backend.tests.test_eligibility.test_lazy_categories_not_scheduled_by_default|test_lazy_categories_not_scheduled_by_default]]
- [[backend.tests.test_eligibility.test_mixed_label_thread_keeps_active_messages_visible|test_mixed_label_thread_keeps_active_messages_visible]]
- [[backend.tests.test_eligibility.test_permanent_delete_marks_excluded_not_destroyed|test_permanent_delete_marks_excluded_not_destroyed]]
- [[backend.tests.test_eligibility.test_scheduling_order_by_category|test_scheduling_order_by_category]]
- [[backend.tests.test_eligibility.test_search_within_category_context|test_search_within_category_context]]
- [[backend.tests.test_eligibility.test_sent_and_draft_are_excluded|test_sent_and_draft_are_excluded]]
- [[backend.tests.test_eligibility.test_spam_state|test_spam_state]]
- [[backend.tests.test_eligibility.test_spam_to_inbox_restores_eligibility|test_spam_to_inbox_restores_eligibility]]
- [[backend.tests.test_eligibility.test_spam_transition_hides_from_projections|test_spam_transition_hides_from_projections]]
- [[backend.tests.test_eligibility.test_spam_wins_over_inbox|test_spam_wins_over_inbox]]
- [[backend.tests.test_eligibility.test_trash_state|test_trash_state]]
- [[backend.tests.test_eligibility.test_updates_with_required_action_eligible_for_semantic_analysis|test_updates_with_required_action_eligible_for_semantic_analysis]]
