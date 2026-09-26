---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_oauth_two_accounts
source: backend/tests/test_oauth_two_accounts.py
status: active
tags: [module, backend]
---

# backend.tests.test_oauth_two_accounts

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_oauth_two_accounts.py`

## Imports

- `AsyncMock` ← `unittest.mock.AsyncMock`
- `TestClient` ← `fastapi.testclient.TestClient`
- `pytest` ← `pytest`

## Functions

- [[backend.tests.test_oauth_two_accounts._complete_callback|_complete_callback]]
- [[backend.tests.test_oauth_two_accounts.isolated_app|isolated_app]]

## Tests

- [[backend.tests.test_oauth_two_accounts.test_reconnect_same_account_is_idempotent|test_reconnect_same_account_is_idempotent]]
- [[backend.tests.test_oauth_two_accounts.test_second_google_identity_creates_separate_row|test_second_google_identity_creates_separate_row]]
