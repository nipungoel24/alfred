---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.get_email_counts
source: backend/app/main.py
line: 810
status: active
tags: [backend, function, endpoint]
---

# get_email_counts

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Live category + mailbox-state counts (DB-derived, never hardcoded).

## Route

`GET /api/emails/counts`

## Location

`backend/app/main.py:810`

## Signature

```python
(account_id: str | None = None)
```

## Parameters

- `account_id` (`str | None`)

## Side Effects

- none statically observed
