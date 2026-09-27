---
type: function
generated: true
language: python
layer: backend
module: backend.app.services.due_dates
qualified_name: backend.app.services.due_dates.normalize_due_at
source: backend/app/services/due_dates.py
line: 306
status: active
tags: [backend, function]
---

# normalize_due_at

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Return a normalised ISO-8601 due timestamp, or ``None``.

## Location

`backend/app/services/due_dates.py:306`

## Signature

```python
(raw: object, reference: datetime | None = None) -> str | None
```

## Parameters

- `raw` (`object`)
- `reference` (`datetime | None`)

## Returns

`str | None`

## Called By

- [[backend.app.schemas._clean_due|_clean_due]]
- [[backend.app.services.task_derivation.derive_tasks|derive_tasks]]
- [[backend.tests.test_task_extraction_contract.test_a_resolvable_relative_offset_is_kept_as_an_instant|test_a_resolvable_relative_offset_is_kept_as_an_instant]]
- [[backend.tests.test_task_extraction_contract.test_calendar_dates_normalise_to_one_iso_shape|test_calendar_dates_normalise_to_one_iso_shape]]
- [[backend.tests.test_task_extraction_contract.test_month_relative_deadline_is_refused_as_ambiguous|test_month_relative_deadline_is_refused_as_ambiguous]]
- [[backend.tests.test_task_extraction_contract.test_task_due_at_is_never_prose|test_task_due_at_is_never_prose]]
- [[backend.tests.test_task_extraction_contract.test_unusable_deadline_becomes_null|test_unusable_deadline_becomes_null]]

## Side Effects

- none statically observed
