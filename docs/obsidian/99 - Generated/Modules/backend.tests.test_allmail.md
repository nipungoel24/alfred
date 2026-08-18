---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_allmail
source: backend/tests/test_allmail.py
status: active
tags: [module, backend]
---

# backend.tests.test_allmail

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_allmail.py`

## Imports

- `Email` ← `backend.app.schemas.Email`
- `EmailAccount` ← `backend.app.schemas.EmailAccount`
- `GmailProvider` ← `backend.app.mail.providers.gmail.GmailProvider`
- `MagicMock` ← `unittest.mock.MagicMock`
- `MailEligibilityPolicy` ← `backend.app.mail.eligibility.MailEligibilityPolicy`
- `Repository` ← `backend.app.db.repositories.Repository`
- `asyncio` ← `asyncio`
- `datetime` ← `datetime.datetime`
- `json` ← `json`
- `patch` ← `unittest.mock.patch`
- `pytest` ← `pytest`
- `timedelta` ← `datetime.timedelta`
- `timezone` ← `datetime.timezone`

## Functions

- [[backend.tests.test_allmail._account|_account]]
- [[backend.tests.test_allmail._base64|_base64]]
- [[backend.tests.test_allmail._detail|_detail]]
- [[backend.tests.test_allmail._email|_email]]
- [[backend.tests.test_allmail.repo|repo]]

## Tests

- [[backend.tests.test_allmail.test_all_scope_excludes_spam_trash_draft_only|test_all_scope_excludes_spam_trash_draft_only]]
- [[backend.tests.test_allmail.test_all_scope_includes_archived|test_all_scope_includes_archived]]
- [[backend.tests.test_allmail.test_all_scope_kind_filters|test_all_scope_kind_filters]]
- [[backend.tests.test_allmail.test_archived_excluded_from_intelligence|test_archived_excluded_from_intelligence]]
- [[backend.tests.test_allmail.test_archived_tasks_not_in_active_projection|test_archived_tasks_not_in_active_projection]]
- [[backend.tests.test_allmail.test_backfill_first_page_and_resume|test_backfill_first_page_and_resume]]
- [[backend.tests.test_allmail.test_backfill_never_requests_spam_trash|test_backfill_never_requests_spam_trash]]
- [[backend.tests.test_allmail.test_backfill_skips_cached_rows_and_updates_labels|test_backfill_skips_cached_rows_and_updates_labels]]
- [[backend.tests.test_allmail.test_category_ignored_in_all_scope|test_category_ignored_in_all_scope]]
- [[backend.tests.test_allmail.test_counts_report_inbox_allmail_excluded|test_counts_report_inbox_allmail_excluded]]
- [[backend.tests.test_allmail.test_draft_excluded_from_all_mail_and_search|test_draft_excluded_from_all_mail_and_search]]
- [[backend.tests.test_allmail.test_inbox_scope_shows_active_inbox_only|test_inbox_scope_shows_active_inbox_only]]
- [[backend.tests.test_allmail.test_pagination_in_all_scope|test_pagination_in_all_scope]]
- [[backend.tests.test_allmail.test_search_covers_archived_not_spam|test_search_covers_archived_not_spam]]
- [[backend.tests.test_allmail.test_sent_visible_but_excluded_from_intelligence|test_sent_visible_but_excluded_from_intelligence]]
