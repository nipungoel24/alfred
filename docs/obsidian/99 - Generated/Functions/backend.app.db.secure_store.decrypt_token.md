---
type: function
generated: true
language: python
layer: database
module: backend.app.db.secure_store
qualified_name: backend.app.db.secure_store.decrypt_token
source: backend/app/db/secure_store.py
line: 162
status: active
tags: [database, function]
---

# decrypt_token

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Decrypt a stored credential.

## Location

`backend/app/db/secure_store.py:162`

## Signature

```python
(enc_data: bytes) -> str
```

## Parameters

- `enc_data` (`bytes`)

## Returns

`str`

## Calls

- `b64decode` (`base64.b64decode`, calls-inferred)

## Called By

- [[backend.app.main._backfill_estimate_once|_backfill_estimate_once]]
- [[backend.app.main._backfill_worker|_backfill_worker]]
- [[backend.app.main._label_backfill|_label_backfill]]
- [[backend.app.main.sync_account|sync_account]]
- [[backend.tests.test_secure_store.TestFailClosed.test_a_corrupt_versioned_blob_raises|test_a_corrupt_versioned_blob_raises]]
- [[backend.tests.test_secure_store.TestFailClosed.test_a_dpapi_decrypt_failure_raises_rather_than_returning_empty|test_a_dpapi_decrypt_failure_raises_rather_than_returning_empty]]
- [[backend.tests.test_secure_store.TestLegacyMigration.test_a_legacy_value_can_be_re_encrypted|test_a_legacy_value_can_be_re_encrypted]]
- [[backend.tests.test_secure_store.TestLegacyMigration.test_a_versioned_blob_is_not_treated_as_legacy|test_a_versioned_blob_is_not_treated_as_legacy]]
- [[backend.tests.test_secure_store.TestLegacyMigration.test_legacy_base64_value_is_still_readable|test_legacy_base64_value_is_still_readable]]
- [[backend.tests.test_secure_store.TestLegacyMigration.test_legacy_value_is_flagged_as_a_security_event|test_legacy_value_is_flagged_as_a_security_event]]
- [[backend.tests.test_secure_store.TestLegacyMigration.test_unreadable_legacy_value_raises|test_unreadable_legacy_value_raises]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_empty_secret_round_trips_to_empty|test_empty_secret_round_trips_to_empty]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_round_trip_returns_the_original_secret|test_round_trip_returns_the_original_secret]]
- [[backend.tests.test_secure_store.TestRealDpapiIsActuallyUsed.test_two_encryptions_of_the_same_value_differ|test_two_encryptions_of_the_same_value_differ]]

## Side Effects

- handles credentials/tokens — see [[Token Security]]
