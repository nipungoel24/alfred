---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.app.services.task_derivation
source: backend/app/services/task_derivation.py
status: active
tags: [module, backend]
---

# backend.app.services.task_derivation

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/app/services/task_derivation.py`

## Imports

- `ActionItem` ← `backend.app.schemas.ActionItem`
- `Email` ← `backend.app.schemas.Email`
- `EmailAnalysis` ← `backend.app.schemas.EmailAnalysis`
- `Task` ← `backend.app.schemas.Task`
- `datetime` ← `datetime.datetime`
- `hashlib` ← `hashlib`
- `re` ← `re`
- `timezone` ← `datetime.timezone`

## Functions

- [[backend.app.services.task_derivation._assign_confidence|_assign_confidence]]
- [[backend.app.services.task_derivation._is_noise|_is_noise]]
- [[backend.app.services.task_derivation._is_user_actionable|_is_user_actionable]]
- [[backend.app.services.task_derivation._normalize_action|_normalize_action]]
- [[backend.app.services.task_derivation.derive_tasks|derive_tasks]]
- [[backend.app.services.task_derivation.rebuild_tasks_from_analyses|rebuild_tasks_from_analyses]]
- [[backend.app.services.task_derivation.task_fingerprint|task_fingerprint]]

## Constants

- `DERIVATION_VERSION`
- `LOW_TASK_CATEGORIES`
- `MIN_TASK_LENGTH`
- `NOISE_PATTERNS`
