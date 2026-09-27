---
type: class
generated: true
language: python
layer: backend
module: backend.app.schemas
qualified_name: backend.app.schemas.Deadline
source: backend/app/schemas.py
line: 45
status: active
tags: [backend, class]
---

# Deadline

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `Deadline` in `backend/app/schemas.py`.

## Location

`backend/app/schemas.py:45`

## Bases

- `BaseModel`

## Called By

- [[backend.tests.test_extended.get_analysis|get_analysis]]
- [[backend.tests.test_extended.test_briefing_deadline_aggregation|test_briefing_deadline_aggregation]]
- [[backend.tests.test_extended.test_explicit_deadline_schema_handling|test_explicit_deadline_schema_handling]]
- [[backend.tests.test_task_derivation.test_derive_tasks_adds_explicit_deadlines|test_derive_tasks_adds_explicit_deadlines]]
- [[backend.tests.test_task_derivation.test_derive_tasks_deduplicates_by_fingerprint|test_derive_tasks_deduplicates_by_fingerprint]]
- [[backend.tests.test_task_derivation.test_derive_tasks_skips_deadline_without_a_readable_moment|test_derive_tasks_skips_deadline_without_a_readable_moment]]
- [[backend.tests.test_task_extraction_contract.test_deadline_that_names_no_action_is_not_a_task|test_deadline_that_names_no_action_is_not_a_task]]
- [[backend.tests.test_task_extraction_contract.test_non_action_titles_are_rejected|test_non_action_titles_are_rejected]]
- [[backend.tests.test_task_extraction_contract.test_real_action_titles_are_kept|test_real_action_titles_are_kept]]
- [[backend.tests.test_task_migration.test_migration_idempotency_and_preservation|test_migration_idempotency_and_preservation]]
- [[backend.tests.test_task_reconcile_idempotency.seed_realistic_backlog|seed_realistic_backlog]]

## Side Effects

- none statically observed
