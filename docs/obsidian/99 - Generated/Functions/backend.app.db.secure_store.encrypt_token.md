---
type: function
generated: true
language: python
layer: database
module: backend.app.db.secure_store
qualified_name: backend.app.db.secure_store.encrypt_token
source: backend/app/db/secure_store.py
line: 132
status: active
tags: [database, function]
---

# encrypt_token

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Encrypt a credential for storage.

## Location

`backend/app/db/secure_store.py:132`

## Signature

```python
(token: str) -> bytes
```

## Parameters

- `token` (`str`)

## Returns

`bytes`

## Called By

- [[backend.app.main.gmail_callback|gmail_callback]]
- [[backend.tests.test_secure_store.TestFailClosed.test_a_dpapi_decrypt_failure_raises_rather_than_returning_empty|test_a_dpapi_decrypt_failure_raises_rather_than_returning_empty]]
- [[backend.tests.test_secure_store.TestFailClosed.test_a_dpapi_encrypt_failure_raises_rather_than_downgrading|test_a_dpapi_encrypt_failure_raises_rather_than_downgrading]]
- [[backend.tests.test_secure_store.TestFailClosed.test_encrypt_raises_when_the_store_is_unavailable|test_encrypt_raises_when_the_store_is_unavailable]]
- [[backend.tests.test_secure_store.TestFailClosed.test_no_credential_is_returned_when_storage_fails|test_no_credential_is_returned_when_storage_fails]]
- [[backend.tests.test_secure_store.TestLegacyMigration.test_a_legacy_value_can_be_re_encrypted|test_a_legacy_value_can_be_re_encrypted]]
- [[backend.tests.test_secure_store.TestLegacyMigration.test_a_versioned_blob_is_not_treated_as_legacy|test_a_versioned_blob_is_not_treated_as_legacy]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_ciphertext_does_not_contain_the_plaintext|test_ciphertext_does_not_contain_the_plaintext]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_empty_secret_round_trips_to_empty|test_empty_secret_round_trips_to_empty]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_round_trip_returns_the_original_secret|test_round_trip_returns_the_original_secret]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_stored_blob_carries_the_format_version|test_stored_blob_carries_the_format_version]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_stored_blob_is_not_reversible_base64|test_stored_blob_is_not_reversible_base64]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_two_encryptions_of_the_same_value_differ|test_two_encryptions_of_the_same_value_differ]]

## Side Effects

- handles credentials/tokens — see [[Token Security]]
