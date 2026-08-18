---
type: class
generated: true
language: python
layer: backend
module: backend.app.schemas
qualified_name: backend.app.schemas.Email
source: backend/app/schemas.py
line: 24
status: active
tags: [backend, class]
---

# Email

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `Email` in `backend/app/schemas.py`.

## Location

`backend/app/schemas.py:24`

## Bases

- `BaseModel`

## Called By

- [[backend.app.mail.normalizer.normalized_email|normalized_email]]
- [[backend.app.mail.providers.gmail.GmailProvider._normalize_message|_normalize_message]]
- [[backend.tests.test_allmail._email|_email]]
- [[backend.tests.test_core.email|email]]
- [[backend.tests.test_eligibility._email|_email]]
- [[backend.tests.test_eligibility.test_search_within_category_context|test_search_within_category_context]]
- [[backend.tests.test_extended.get_email|get_email]]
- [[backend.tests.test_extended.test_prompt_injection_safety|test_prompt_injection_safety]]
- [[backend.tests.test_gmail_mock.test_gmail_sync_incremental|test_gmail_sync_incremental]]
- [[backend.tests.test_ollama_mock.test_ai_service_analyze_email_success|test_ai_service_analyze_email_success]]
- [[backend.tests.test_task_derivation.test_derive_tasks_adds_explicit_deadlines|test_derive_tasks_adds_explicit_deadlines]]
- [[backend.tests.test_task_derivation.test_derive_tasks_deduplicates_by_fingerprint|test_derive_tasks_deduplicates_by_fingerprint]]
- [[backend.tests.test_task_derivation.test_derive_tasks_ignores_newsletters_unless_urgent|test_derive_tasks_ignores_newsletters_unless_urgent]]
- [[backend.tests.test_task_derivation.test_derive_tasks_ignores_noise|test_derive_tasks_ignores_noise]]
- [[backend.tests.test_task_derivation.test_derive_tasks_ignores_third_party_owner|test_derive_tasks_ignores_third_party_owner]]
- [[backend.tests.test_task_migration.test_migration_idempotency_and_preservation|test_migration_idempotency_and_preservation]]
- [[backend.tests.test_task_migration.test_migration_rollback|test_migration_rollback]]

## Side Effects

- none statically observed
