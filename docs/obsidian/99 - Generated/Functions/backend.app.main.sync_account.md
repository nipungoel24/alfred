---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.sync_account
source: backend/app/main.py
line: 611
status: active
tags: [backend, function, critical-path, endpoint]
---

# sync_account

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `sync_account` in `backend/app/main.py`.

## Route

`POST /api/accounts/{account_id}/sync`

## Location

`backend/app/main.py:611`

## Signature

```python
(account_id: str, load_older: bool = Query(False))
```

## Parameters

- `account_id` (`str`)
- `load_older` (`bool`)

## Calls

- [[backend.app.db.secure_store.decrypt_token|decrypt_token]] (calls)
- [[backend.app.mail.backfill.dump_cursor|dump_cursor]] (calls)
- [[backend.app.mail.backfill.normalize_cursor|normalize_cursor]] (calls)
- [[backend.app.mail.backfill.set_state|set_state]] (calls)
- [[backend.app.mail.eligibility.MailEligibilityPolicy.analysis_queue_priority|analysis_queue_priority]] (calls)
- [[backend.app.mail.eligibility.MailEligibilityPolicy.is_unread|is_unread]] (calls)
- [[backend.app.mail.eligibility.MailEligibilityPolicy.should_schedule_analysis|should_schedule_analysis]] (calls)
- [[backend.app.mail.fingerprint.content_fingerprint|content_fingerprint]] (calls)
- `HTTPException` (`fastapi.HTTPException`, calls-inferred)

## Side Effects

- async I/O
