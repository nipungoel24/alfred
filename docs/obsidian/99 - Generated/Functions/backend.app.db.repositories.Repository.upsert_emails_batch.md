---
type: function
generated: true
language: python
layer: database
module: backend.app.db.repositories.Repository
qualified_name: backend.app.db.repositories.Repository.upsert_emails_batch
source: backend/app/db/repositories.py
line: 67
status: active
tags: [database, function]
---

# upsert_emails_batch

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Batch insert/update emails in a single transaction.

## Location

`backend/app/db/repositories.py:67`

## Signature

```python
(self, email_fingerprint_pairs: list[tuple[Email, str]])
```

## Parameters

- `self`
- `email_fingerprint_pairs` (`list[tuple[Email, str]]`)

## Calls

- [[backend.app.db.database.transaction|transaction]] (calls)

## Side Effects

- none statically observed
