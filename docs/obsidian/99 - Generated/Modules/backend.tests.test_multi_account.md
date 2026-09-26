---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_multi_account
source: backend/tests/test_multi_account.py
status: active
tags: [module, backend]
---

# backend.tests.test_multi_account

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_multi_account.py`

## Imports

- `Category` ← `backend.app.schemas.Category`
- `Email` ← `backend.app.schemas.Email`
- `EmailAnalysis` ← `backend.app.schemas.EmailAnalysis`
- `GmailProvider` ← `backend.app.mail.providers.gmail.GmailProvider`
- `Path` ← `pathlib.Path`
- `Priority` ← `backend.app.schemas.Priority`
- `Repository` ← `backend.app.db.repositories.Repository`
- `SearchFilters` ← `backend.app.schemas.SearchFilters`
- `Task` ← `backend.app.schemas.Task`
- `base64` ← `base64`
- `provider_message_id` ← `backend.app.mail.identity.provider_message_id`
- `scoped_email_id` ← `backend.app.mail.identity.scoped_email_id`

## Functions

- [[backend.tests.test_multi_account.make_analysis|make_analysis]]
- [[backend.tests.test_multi_account.make_email|make_email]]
- [[backend.tests.test_multi_account.test_same_provider_message_id_collision.gmail_detail|gmail_detail]]

## Tests

- [[backend.tests.test_multi_account.test_account_credentials_isolation|test_account_credentials_isolation]]
- [[backend.tests.test_multi_account.test_account_id_stored_correctly|test_account_id_stored_correctly]]
- [[backend.tests.test_multi_account.test_account_prefixed_email_ids|test_account_prefixed_email_ids]]
- [[backend.tests.test_multi_account.test_account_specific_counts|test_account_specific_counts]]
- [[backend.tests.test_multi_account.test_delete_email_by_account|test_delete_email_by_account]]
- [[backend.tests.test_multi_account.test_emails_missing_labels_by_account|test_emails_missing_labels_by_account]]
- [[backend.tests.test_multi_account.test_label_update_by_account|test_label_update_by_account]]
- [[backend.tests.test_multi_account.test_same_provider_message_id_collision|test_same_provider_message_id_collision]]
- [[backend.tests.test_multi_account.test_search_respects_account_isolation|test_search_respects_account_isolation]]
