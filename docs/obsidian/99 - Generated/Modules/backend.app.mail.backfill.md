---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.app.mail.backfill
source: backend/app/mail/backfill.py
status: active
tags: [module, backend]
---

# backend.app.mail.backfill

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/app/mail/backfill.py`

## Imports

- `BackfillState` ← `backend.app.mail.eligibility.BackfillState`
- `datetime` ← `datetime.datetime`
- `json` ← `json`
- `timezone` ← `datetime.timezone`

## Functions

- [[backend.app.mail.backfill.dump_cursor|dump_cursor]]
- [[backend.app.mail.backfill.normalize_cursor|normalize_cursor]]
- [[backend.app.mail.backfill.record_failure|record_failure]]
- [[backend.app.mail.backfill.record_success|record_success]]
- [[backend.app.mail.backfill.set_state|set_state]]
- [[backend.app.mail.backfill.status_payload|status_payload]]

## Constants

- `BACKFILL_CURSOR_FIELDS`
- `VALID_STATES`
