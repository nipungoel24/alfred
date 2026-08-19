---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_desktop_auth
source: backend/tests/test_desktop_auth.py
status: active
tags: [module, backend]
---

# backend.tests.test_desktop_auth

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_desktop_auth.py`

## Imports

- `Path` ← `pathlib.Path`
- `TestClient` ← `fastapi.testclient.TestClient`
- `json` ← `json`
- `os` ← `os`
- `pytest` ← `pytest`
- `sqlite3` ← `sqlite3`

## Functions

- [[backend.tests.test_desktop_auth.authed_app|authed_app]]

## Tests

- [[backend.tests.test_desktop_auth.test_api_requires_token|test_api_requires_token]]
- [[backend.tests.test_desktop_auth.test_health_requires_token_when_enabled|test_health_requires_token_when_enabled]]
- [[backend.tests.test_desktop_auth.test_no_token_means_no_auth|test_no_token_means_no_auth]]
- [[backend.tests.test_desktop_auth.test_oauth_callback_is_exempt_from_token|test_oauth_callback_is_exempt_from_token]]
- [[backend.tests.test_desktop_auth.test_query_token_form_for_sse|test_query_token_form_for_sse]]
- [[backend.tests.test_desktop_auth.test_shutdown_endpoint_is_token_protected|test_shutdown_endpoint_is_token_protected]]
