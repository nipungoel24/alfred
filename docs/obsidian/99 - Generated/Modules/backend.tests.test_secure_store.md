---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_secure_store
source: backend/tests/test_secure_store.py
status: active
tags: [module, backend]
---

# backend.tests.test_secure_store

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_secure_store.py`

## Imports

- `FORMAT_VERSION` ← `backend.app.db.secure_store.FORMAT_VERSION`
- `SecureStoreUnavailable` ← `backend.app.db.secure_store.SecureStoreUnavailable`
- `base64` ← `base64`
- `decrypt_token` ← `backend.app.db.secure_store.decrypt_token`
- `encrypt_token` ← `backend.app.db.secure_store.encrypt_token`
- `is_available` ← `backend.app.db.secure_store.is_available`
- `pytest` ← `pytest`
- `secure_store` ← `backend.app.db.secure_store`
- `status` ← `backend.app.db.secure_store.status`
- `sys` ← `sys`

## Classes

- [[backend.tests.test_secure_store.TestFailClosed|TestFailClosed]]
- [[backend.tests.test_secure_store.TestHealthReporting|TestHealthReporting]]
- [[backend.tests.test_secure_store.TestLegacyMigration|TestLegacyMigration]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed|TestRealDpapiIsActuallyUsed]]

## Functions

- [[backend.tests.test_secure_store.TestFailClosed.test_a_dpapi_encrypt_failure_raises_rather_than_downgrading.boom|boom]]

## Tests

- [[backend.tests.test_secure_store.TestFailClosed.test_a_corrupt_versioned_blob_raises|test_a_corrupt_versioned_blob_raises]]
- [[backend.tests.test_secure_store.TestFailClosed.test_a_dpapi_decrypt_failure_raises_rather_than_returning_empty|test_a_dpapi_decrypt_failure_raises_rather_than_returning_empty]]
- [[backend.tests.test_secure_store.TestFailClosed.test_a_dpapi_encrypt_failure_raises_rather_than_downgrading|test_a_dpapi_encrypt_failure_raises_rather_than_downgrading]]
- [[backend.tests.test_secure_store.TestFailClosed.test_encrypt_raises_when_the_store_is_unavailable|test_encrypt_raises_when_the_store_is_unavailable]]
- [[backend.tests.test_secure_store.TestFailClosed.test_no_credential_is_returned_when_storage_fails|test_no_credential_is_returned_when_storage_fails]]
- [[backend.tests.test_secure_store.TestFailClosed.test_status_reports_unavailable_when_dpapi_is_missing|test_status_reports_unavailable_when_dpapi_is_missing]]
- [[backend.tests.test_secure_store.TestHealthReporting.test_health_reports_a_single_known_state|test_health_reports_a_single_known_state]]
- [[backend.tests.test_secure_store.TestLegacyMigration.test_a_legacy_value_can_be_re_encrypted|test_a_legacy_value_can_be_re_encrypted]]
- [[backend.tests.test_secure_store.TestLegacyMigration.test_a_versioned_blob_is_not_treated_as_legacy|test_a_versioned_blob_is_not_treated_as_legacy]]
- [[backend.tests.test_secure_store.TestLegacyMigration.test_legacy_base64_value_is_still_readable|test_legacy_base64_value_is_still_readable]]
- [[backend.tests.test_secure_store.TestLegacyMigration.test_legacy_value_is_flagged_as_a_security_event|test_legacy_value_is_flagged_as_a_security_event]]
- [[backend.tests.test_secure_store.TestLegacyMigration.test_unreadable_legacy_value_raises|test_unreadable_legacy_value_raises]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_availability_probe_succeeds_on_windows|test_availability_probe_succeeds_on_windows]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_ciphertext_does_not_contain_the_plaintext|test_ciphertext_does_not_contain_the_plaintext]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_empty_secret_round_trips_to_empty|test_empty_secret_round_trips_to_empty]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_round_trip_returns_the_original_secret|test_round_trip_returns_the_original_secret]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_stored_blob_carries_the_format_version|test_stored_blob_carries_the_format_version]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_stored_blob_is_not_reversible_base64|test_stored_blob_is_not_reversible_base64]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_two_encryptions_of_the_same_value_differ|test_two_encryptions_of_the_same_value_differ]]
