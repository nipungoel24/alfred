---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.app.services.due_dates
source: backend/app/services/due_dates.py
status: active
tags: [module, backend]
---

# backend.app.services.due_dates

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/app/services/due_dates.py`

## Imports

- `annotations` ← `__future__.annotations`
- `date` ← `datetime.date`
- `datetime` ← `datetime.datetime`
- `re` ← `re`
- `timedelta` ← `datetime.timedelta`
- `timezone` ← `datetime.timezone`

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

## Constants

- `VAGUE_DUE_PHRASES`
- `_BARE_TIME_RE`
- `_DMY_NO_YEAR_RE`
- `_DMY_RE`
- `_FIELD_LABEL_BARE_RE`
- `_FIELD_LABEL_RE`
- `_ISO_DATETIME_RE`
- `_ISO_DATE_RE`
- `_MDY_NO_YEAR_RE`
- `_MDY_RE`
- `_MONTHS`
- `_MONTH_ALT`
- `_NON_ACTION_RE`
- `_ORDINAL_SUFFIX_RE`
- `_RELATIVE_RE`
- `_TEMPORAL_FILLER_RE`
- `_TEMPORAL_TOKEN_RE`
- `_UNIT_SECONDS`
- `_VAGUE_RE`
- `_WEEKDAY_GLOSS_RE`
