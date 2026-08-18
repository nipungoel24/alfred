---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.upsert_email
source: backend/app/db/repositories.py
line: 35
status: active
tags: [database, function, critical-path]
---

# upsert_email

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Insert or update a single email. Caller manages transaction.

## Location

`backend/app/db/repositories.py:35`

## Signature

```python
(self, email: Email, fingerprint: str)
```

## Parameters

- `self`
- `email` (`Email`)
- `fingerprint` (`str`)

## Calls

- `model_dump_json` (`backend.app.db.repositories.Repository.email.model_dump_json`, calls-inferred)
- `isoformat` (`backend.app.db.repositories.Repository.email.received_at.isoformat`, calls-inferred)
- `lower` (`backend.app.db.repositories.Repository.email.sender.lower`, calls-inferred)
- [[backend.app.mail.eligibility.MailEligibilityPolicy.pipeline_eligibility|pipeline_eligibility]] (calls)
- [[backend.app.mail.eligibility.gmail_category_from_labels|gmail_category_from_labels]] (calls)
- [[backend.app.mail.eligibility.mailbox_state_from_labels|mailbox_state_from_labels]] (calls)
- `now` (`datetime.datetime.now`, calls-inferred)
- `dumps` (`json.dumps`, calls-inferred)

## Called By

- [[backend.app.mail.providers.gmail.GmailProvider.backfill_messages|backfill_messages]]
- [[backend.app.mail.providers.gmail.GmailProvider.sync_messages|sync_messages]]
- [[backend.tests.test_allmail.test_all_scope_excludes_spam_trash_draft_only|test_all_scope_excludes_spam_trash_draft_only]]
- [[backend.tests.test_allmail.test_all_scope_includes_archived|test_all_scope_includes_archived]]
- [[backend.tests.test_allmail.test_all_scope_kind_filters|test_all_scope_kind_filters]]
- [[backend.tests.test_allmail.test_archived_excluded_from_intelligence|test_archived_excluded_from_intelligence]]
- [[backend.tests.test_allmail.test_archived_tasks_not_in_active_projection|test_archived_tasks_not_in_active_projection]]
- [[backend.tests.test_allmail.test_backfill_skips_cached_rows_and_updates_labels|test_backfill_skips_cached_rows_and_updates_labels]]
- [[backend.tests.test_allmail.test_category_ignored_in_all_scope|test_category_ignored_in_all_scope]]
- [[backend.tests.test_allmail.test_counts_report_inbox_allmail_excluded|test_counts_report_inbox_allmail_excluded]]
- [[backend.tests.test_allmail.test_draft_excluded_from_all_mail_and_search|test_draft_excluded_from_all_mail_and_search]]
- [[backend.tests.test_allmail.test_inbox_scope_shows_active_inbox_only|test_inbox_scope_shows_active_inbox_only]]
- [[backend.tests.test_allmail.test_pagination_in_all_scope|test_pagination_in_all_scope]]
- [[backend.tests.test_allmail.test_search_covers_archived_not_spam|test_search_covers_archived_not_spam]]
- [[backend.tests.test_allmail.test_sent_visible_but_excluded_from_intelligence|test_sent_visible_but_excluded_from_intelligence]]
- [[backend.tests.test_eligibility.test_active_tasks_exclude_spam_sourced|test_active_tasks_exclude_spam_sourced]]
- [[backend.tests.test_eligibility.test_category_counts_derive_from_labels|test_category_counts_derive_from_labels]]
- [[backend.tests.test_eligibility.test_category_filter_is_db_driven|test_category_filter_is_db_driven]]
- [[backend.tests.test_eligibility.test_email_api_excluded_mail_never_listed|test_email_api_excluded_mail_never_listed]]
- [[backend.tests.test_eligibility.test_history_label_changes_refresh_via_metadata|test_history_label_changes_refresh_via_metadata]]
- [[backend.tests.test_eligibility.test_label_only_history_update_recomputes_state|test_label_only_history_update_recomputes_state]]
- [[backend.tests.test_eligibility.test_mixed_label_thread_keeps_active_messages_visible|test_mixed_label_thread_keeps_active_messages_visible]]
- [[backend.tests.test_eligibility.test_permanent_delete_marks_excluded_not_destroyed|test_permanent_delete_marks_excluded_not_destroyed]]
- [[backend.tests.test_eligibility.test_search_within_category_context|test_search_within_category_context]]
- [[backend.tests.test_eligibility.test_spam_transition_hides_from_projections|test_spam_transition_hides_from_projections]]

## Writes

- [[table_emails]]

## Side Effects

- SQLite
