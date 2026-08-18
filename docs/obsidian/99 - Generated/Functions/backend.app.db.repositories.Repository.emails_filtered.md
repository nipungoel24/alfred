---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.emails_filtered
source: backend/app/db/repositories.py
line: 192
status: active
tags: [database, function]
---

# emails_filtered

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Fetch emails with typed filters, DB-side (no JS filtering).

## Location

`backend/app/db/repositories.py:192`

## Signature

```python
(self, account_id: str | None = None, category: str | None = None, mailbox_state: str | None = None, scope: str = 'inbox', kind: str | None = None, include_excluded: bool = False, query: str | None = None, limit: int = 200, offset: int = 0) -> list[Email]
```

## Parameters

- `self`
- `account_id` (`str | None`)
- `category` (`str | None`)
- `mailbox_state` (`str | None`)
- `scope` (`str`)
- `kind` (`str | None`)
- `include_excluded` (`bool`)
- `query` (`str | None`)
- `limit` (`int`)
- `offset` (`int`)

## Returns

`list[Email]`

## Calls

- `model_validate_json` (`backend.app.schemas.Email.model_validate_json`, calls-inferred)

## Called By

- [[backend.tests.test_allmail.test_all_scope_excludes_spam_trash_draft_only|test_all_scope_excludes_spam_trash_draft_only]]
- [[backend.tests.test_allmail.test_all_scope_includes_archived|test_all_scope_includes_archived]]
- [[backend.tests.test_allmail.test_all_scope_kind_filters|test_all_scope_kind_filters]]
- [[backend.tests.test_allmail.test_archived_excluded_from_intelligence|test_archived_excluded_from_intelligence]]
- [[backend.tests.test_allmail.test_category_ignored_in_all_scope|test_category_ignored_in_all_scope]]
- [[backend.tests.test_allmail.test_draft_excluded_from_all_mail_and_search|test_draft_excluded_from_all_mail_and_search]]
- [[backend.tests.test_allmail.test_inbox_scope_shows_active_inbox_only|test_inbox_scope_shows_active_inbox_only]]
- [[backend.tests.test_allmail.test_pagination_in_all_scope|test_pagination_in_all_scope]]
- [[backend.tests.test_allmail.test_sent_visible_but_excluded_from_intelligence|test_sent_visible_but_excluded_from_intelligence]]
- [[backend.tests.test_eligibility.test_category_filter_is_db_driven|test_category_filter_is_db_driven]]
- [[backend.tests.test_eligibility.test_mixed_label_thread_keeps_active_messages_visible|test_mixed_label_thread_keeps_active_messages_visible]]
- [[backend.tests.test_eligibility.test_search_within_category_context|test_search_within_category_context]]
- [[backend.tests.test_eligibility.test_spam_transition_hides_from_projections|test_spam_transition_hides_from_projections]]

## Reads

- [[table_emails]]

## Side Effects

- SQLite
