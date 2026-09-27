---
type: class
generated: true
language: python
layer: backend
module: backend.app.schemas
qualified_name: backend.app.schemas.ActionItem
source: backend/app/schemas.py
line: 38
status: active
tags: [backend, class]
---

# ActionItem

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `ActionItem` in `backend/app/schemas.py`.

## Location

`backend/app/schemas.py:38`

## Bases

- `BaseModel`

## Called By

- [[backend.tests.test_task_derivation.test_derive_tasks_deduplicates_by_fingerprint|test_derive_tasks_deduplicates_by_fingerprint]]
- [[backend.tests.test_task_derivation.test_derive_tasks_drops_unresolvable_deadline|test_derive_tasks_drops_unresolvable_deadline]]
- [[backend.tests.test_task_derivation.test_derive_tasks_ignores_newsletters_unless_urgent|test_derive_tasks_ignores_newsletters_unless_urgent]]
- [[backend.tests.test_task_derivation.test_derive_tasks_ignores_noise|test_derive_tasks_ignores_noise]]
- [[backend.tests.test_task_derivation.test_derive_tasks_ignores_third_party_owner|test_derive_tasks_ignores_third_party_owner]]
- [[backend.tests.test_task_extraction_contract.test_actionable_email_produces_the_action_as_the_title|test_actionable_email_produces_the_action_as_the_title]]
- [[backend.tests.test_task_extraction_contract.test_date_becomes_due_at_not_the_title|test_date_becomes_due_at_not_the_title]]
- [[backend.tests.test_task_extraction_contract.test_missing_due_date_is_null|test_missing_due_date_is_null]]
- [[backend.tests.test_task_extraction_contract.test_no_action_required_creates_no_task|test_no_action_required_creates_no_task]]
- [[backend.tests.test_task_extraction_contract.test_owner_is_not_encoded_into_description|test_owner_is_not_encoded_into_description]]
- [[backend.tests.test_task_extraction_contract.test_priority_is_taken_from_the_analysis|test_priority_is_taken_from_the_analysis]]
- [[backend.tests.test_task_extraction_contract.test_pure_noise_creates_no_task|test_pure_noise_creates_no_task]]
- [[backend.tests.test_task_extraction_contract.test_receipt_creates_no_task|test_receipt_creates_no_task]]
- [[backend.tests.test_task_extraction_contract.test_relative_deadline_resolves_against_the_message_timestamp|test_relative_deadline_resolves_against_the_message_timestamp]]
- [[backend.tests.test_task_extraction_contract.test_relative_deadline_without_a_reference_stays_null|test_relative_deadline_without_a_reference_stays_null]]
- [[backend.tests.test_task_extraction_contract.test_relative_form_survives_the_schema_but_resolves_in_derivation|test_relative_form_survives_the_schema_but_resolves_in_derivation]]
- [[backend.tests.test_task_extraction_contract.test_source_linkage_is_preserved|test_source_linkage_is_preserved]]
- [[backend.tests.test_task_extraction_contract.test_task_due_at_is_never_prose|test_task_due_at_is_never_prose]]
- [[backend.tests.test_task_extraction_contract.test_unusable_deadline_becomes_null|test_unusable_deadline_becomes_null]]
- [[backend.tests.test_task_migration.test_migration_idempotency_and_preservation|test_migration_idempotency_and_preservation]]

## Side Effects

- none statically observed
