---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.account
source: backend/app/db/repositories.py
line: 459
status: active
tags: [database, function]
---

# account

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `account` in `backend/app/db/repositories.py`.

## Location

`backend/app/db/repositories.py:459`

## Signature

```python
(self, account_id: str)
```

## Parameters

- `self`
- `account_id` (`str`)

## Calls

- [[backend.app.schemas.EmailAccount|EmailAccount]] (calls)

## Called By

- [[backend.tests.test_allmail.test_backfill_first_page_and_resume|test_backfill_first_page_and_resume]]

## Reads

- [[table_accounts]]

## Side Effects

- SQLite
