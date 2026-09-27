---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.tests.test_task_extraction_contract
source: backend/tests/test_task_extraction_contract.py
status: active
tags: [module, backend]
---

# backend.tests.test_task_extraction_contract

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/tests/test_task_extraction_contract.py`

## Imports

- `ActionItem` ← `backend.app.schemas.ActionItem`
- `Category` ← `backend.app.schemas.Category`
- `Deadline` ← `backend.app.schemas.Deadline`
- `Email` ← `backend.app.schemas.Email`
- `EmailAnalysis` ← `backend.app.schemas.EmailAnalysis`
- `Priority` ← `backend.app.schemas.Priority`
- `Task` ← `backend.app.schemas.Task`
- `ValidationError` ← `pydantic.ValidationError`
- `datetime` ← `datetime.datetime`
- `derive_tasks` ← `backend.app.services.task_derivation.derive_tasks`
- `is_temporal_only` ← `backend.app.services.due_dates.is_temporal_only`
- `normalize_due_at` ← `backend.app.services.due_dates.normalize_due_at`
- `pytest` ← `pytest`
- `timezone` ← `datetime.timezone`

## Functions

- [[backend.tests.test_task_extraction_contract.make_analysis|make_analysis]]
- [[backend.tests.test_task_extraction_contract.make_email|make_email]]

## Tests

- [[backend.tests.test_task_extraction_contract.test_a_resolvable_relative_offset_is_kept_as_an_instant|test_a_resolvable_relative_offset_is_kept_as_an_instant]]
- [[backend.tests.test_task_extraction_contract.test_actionable_email_produces_the_action_as_the_title|test_actionable_email_produces_the_action_as_the_title]]
- [[backend.tests.test_task_extraction_contract.test_calendar_dates_normalise_to_one_iso_shape|test_calendar_dates_normalise_to_one_iso_shape]]
- [[backend.tests.test_task_extraction_contract.test_date_becomes_due_at_not_the_title|test_date_becomes_due_at_not_the_title]]
- [[backend.tests.test_task_extraction_contract.test_deadline_that_names_no_action_is_not_a_task|test_deadline_that_names_no_action_is_not_a_task]]
- [[backend.tests.test_task_extraction_contract.test_malformed_model_output_is_rejected|test_malformed_model_output_is_rejected]]
- [[backend.tests.test_task_extraction_contract.test_missing_due_date_is_null|test_missing_due_date_is_null]]
- [[backend.tests.test_task_extraction_contract.test_month_relative_deadline_is_refused_as_ambiguous|test_month_relative_deadline_is_refused_as_ambiguous]]
- [[backend.tests.test_task_extraction_contract.test_no_action_required_creates_no_task|test_no_action_required_creates_no_task]]
- [[backend.tests.test_task_extraction_contract.test_non_action_titles_are_rejected|test_non_action_titles_are_rejected]]
- [[backend.tests.test_task_extraction_contract.test_owner_is_not_encoded_into_description|test_owner_is_not_encoded_into_description]]
- [[backend.tests.test_task_extraction_contract.test_priority_is_taken_from_the_analysis|test_priority_is_taken_from_the_analysis]]
- [[backend.tests.test_task_extraction_contract.test_pure_noise_creates_no_task|test_pure_noise_creates_no_task]]
- [[backend.tests.test_task_extraction_contract.test_real_action_titles_are_kept|test_real_action_titles_are_kept]]
- [[backend.tests.test_task_extraction_contract.test_receipt_creates_no_task|test_receipt_creates_no_task]]
- [[backend.tests.test_task_extraction_contract.test_relative_deadline_resolves_against_the_message_timestamp|test_relative_deadline_resolves_against_the_message_timestamp]]
- [[backend.tests.test_task_extraction_contract.test_relative_deadline_without_a_reference_stays_null|test_relative_deadline_without_a_reference_stays_null]]
- [[backend.tests.test_task_extraction_contract.test_relative_form_survives_the_schema_but_resolves_in_derivation|test_relative_form_survives_the_schema_but_resolves_in_derivation]]
- [[backend.tests.test_task_extraction_contract.test_source_linkage_is_preserved|test_source_linkage_is_preserved]]
- [[backend.tests.test_task_extraction_contract.test_task_due_at_is_never_prose|test_task_due_at_is_never_prose]]
- [[backend.tests.test_task_extraction_contract.test_unusable_deadline_becomes_null|test_unusable_deadline_becomes_null]]

## Constants

- `RECEIVED`
