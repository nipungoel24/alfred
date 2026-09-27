---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.app.schemas
source: backend/app/schemas.py
status: active
tags: [module, backend]
---

# backend.app.schemas

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/app/schemas.py`

## Imports

- `Any` ← `typing.Any`
- `BaseModel` ← `pydantic.BaseModel`
- `Enum` ← `enum.Enum`
- `Field` ← `pydantic.Field`
- `datetime` ← `datetime.datetime`
- `field_validator` ← `pydantic.field_validator`
- `is_relative_expression` ← `backend.app.services.due_dates.is_relative_expression`
- `normalize_due_at` ← `backend.app.services.due_dates.normalize_due_at`

## Classes

- [[backend.app.schemas.ActionItem|ActionItem]]
- [[backend.app.schemas.BriefingItem|BriefingItem]]
- [[backend.app.schemas.Category|Category]]
- [[backend.app.schemas.Deadline|Deadline]]
- [[backend.app.schemas.Email|Email]]
- [[backend.app.schemas.EmailAccount|EmailAccount]]
- [[backend.app.schemas.EmailAnalysis|EmailAnalysis]]
- [[backend.app.schemas.ErrorDetail|ErrorDetail]]
- [[backend.app.schemas.InboxBriefing|InboxBriefing]]
- [[backend.app.schemas.Priority|Priority]]
- [[backend.app.schemas.SearchFilters|SearchFilters]]
- [[backend.app.schemas.Task|Task]]
- [[backend.app.schemas.TaskPriorityPatch|TaskPriorityPatch]]

## Functions

- [[backend.app.schemas.SearchFilters._resolve_mailbox_state|_resolve_mailbox_state]]
- [[backend.app.schemas._clean_due|_clean_due]]

## Constants

- `IN_SCOPE_TO_MAILBOX_STATE`
- `_DUE_CONTRACT`
