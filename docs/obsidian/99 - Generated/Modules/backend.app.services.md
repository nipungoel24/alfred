---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.app.services
source: backend/app/services/__init__.py
status: active
tags: [module, backend]
---

# backend.app.services

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/app/services/__init__.py`

## Classes

- [[backend.app.services.task_derivation.ReconcileReport|ReconcileReport]]
- [[backend.app.services.task_migration.TaskMigrationService|TaskMigrationService]]

## Functions

- [[backend.app.services.due_dates._has_temporal_token|_has_temporal_token]]
- [[backend.app.services.due_dates._is_definitely_not_a_date|_is_definitely_not_a_date]]
- [[backend.app.services.due_dates._iso_from_parts|_iso_from_parts]]
- [[backend.app.services.due_dates._month_number|_month_number]]
- [[backend.app.services.due_dates._resolve_calendar|_resolve_calendar]]
- [[backend.app.services.due_dates._resolve_relative|_resolve_relative]]
- [[backend.app.services.due_dates._strip_wrapping|_strip_wrapping]]
- [[backend.app.services.due_dates.is_non_action|is_non_action]]
- [[backend.app.services.due_dates.is_relative_expression|is_relative_expression]]
- [[backend.app.services.due_dates.is_temporal_only|is_temporal_only]]
- [[backend.app.services.due_dates.normalize_due_at|normalize_due_at]]
- [[backend.app.services.task_derivation.ReconcileReport.as_dict|as_dict]]
- [[backend.app.services.task_derivation._assign_confidence|_assign_confidence]]
- [[backend.app.services.task_derivation._is_derived_change|_is_derived_change]]
- [[backend.app.services.task_derivation._is_noise|_is_noise]]
- [[backend.app.services.task_derivation._is_user_actionable|_is_user_actionable]]
- [[backend.app.services.task_derivation._normalize_action|_normalize_action]]
- [[backend.app.services.task_derivation._reference|_reference]]
- [[backend.app.services.task_derivation.candidate_fingerprints|candidate_fingerprints]]
- [[backend.app.services.task_derivation.derive_tasks|derive_tasks]]
- [[backend.app.services.task_derivation.rebuild_tasks_from_analyses|rebuild_tasks_from_analyses]]
- [[backend.app.services.task_derivation.reconcile_tasks_from_analyses|reconcile_tasks_from_analyses]]
- [[backend.app.services.task_derivation.task_fingerprint|task_fingerprint]]
- [[backend.app.services.task_migration.TaskMigrationService.__init__|__init__]]
- [[backend.app.services.task_migration.TaskMigrationService.run_migration|run_migration]]
