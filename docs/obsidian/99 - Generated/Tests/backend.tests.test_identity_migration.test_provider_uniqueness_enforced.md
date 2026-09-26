---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_identity_migration
qualified_name: backend.tests.test_identity_migration.test_provider_uniqueness_enforced
source: backend/tests/test_identity_migration.py
line: 234
status: active
tags: [test, function, test]
---

# test_provider_uniqueness_enforced

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Duplicate (account_id, provider_message_id) rows are rejected.

## Location

`backend/tests/test_identity_migration.py:234`

## Signature

```python
(tmp_path: Path)
```

## Parameters

- `tmp_path` (`Path`)

## Calls

- [[backend.app.db.repositories.Repository|Repository]] (calls)
- [[backend.app.mail.identity.scoped_email_id|scoped_email_id]] (calls)
- [[backend.app.schemas.Email|Email]] (calls)
- `raises` (`pytest.raises`, calls-inferred)

## Writes

- [[table_emails]]

## Side Effects

- SQLite
