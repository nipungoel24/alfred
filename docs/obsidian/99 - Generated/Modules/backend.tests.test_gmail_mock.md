---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_gmail_mock
source: backend/tests/test_gmail_mock.py
status: active
tags: [module, backend]
---

# backend.tests.test_gmail_mock

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_gmail_mock.py`

## Imports

- `ActionItem` ← `backend.app.schemas.ActionItem`
- `AsyncMock` ← `unittest.mock.AsyncMock`
- `Category` ← `backend.app.schemas.Category`
- `Deadline` ← `backend.app.schemas.Deadline`
- `Email` ← `backend.app.schemas.Email`
- `EmailAccount` ← `backend.app.schemas.EmailAccount`
- `EmailAnalysis` ← `backend.app.schemas.EmailAnalysis`
- `GmailProvider` ← `backend.app.mail.providers.gmail.GmailProvider`
- `MagicMock` ← `unittest.mock.MagicMock`
- `Priority` ← `backend.app.schemas.Priority`
- `Repository` ← `backend.app.db.repositories.Repository`
- `asyncio` ← `asyncio`
- `datetime` ← `datetime.datetime`
- `decrypt_token` ← `backend.app.db.secure_store.decrypt_token`
- `encrypt_token` ← `backend.app.db.secure_store.encrypt_token`
- `httpx` ← `httpx`
- `json` ← `json`
- `patch` ← `unittest.mock.patch`
- `pytest` ← `pytest`
- `timedelta` ← `datetime.timedelta`
- `timezone` ← `datetime.timezone`

## Functions

- [[backend.tests.test_gmail_mock.base64_encode_string|base64_encode_string]]
- [[backend.tests.test_gmail_mock.mock_gmail|mock_gmail]]
- [[backend.tests.test_gmail_mock.temp_repo|temp_repo]]

## Tests

- [[backend.tests.test_gmail_mock.test_gmail_html_sanitisation|test_gmail_html_sanitisation]]
- [[backend.tests.test_gmail_mock.test_gmail_oauth_url_generation|test_gmail_oauth_url_generation]]
- [[backend.tests.test_gmail_mock.test_gmail_sync_history_expired_recovery|test_gmail_sync_history_expired_recovery]]
- [[backend.tests.test_gmail_mock.test_gmail_sync_incremental|test_gmail_sync_incremental]]
- [[backend.tests.test_gmail_mock.test_gmail_sync_initial|test_gmail_sync_initial]]
- [[backend.tests.test_gmail_mock.test_gmail_sync_load_older|test_gmail_sync_load_older]]
- [[backend.tests.test_gmail_mock.test_gmail_token_exchange|test_gmail_token_exchange]]
