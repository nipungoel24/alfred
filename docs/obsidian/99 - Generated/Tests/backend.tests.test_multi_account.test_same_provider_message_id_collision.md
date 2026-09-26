---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_multi_account
qualified_name: backend.tests.test_multi_account.test_same_provider_message_id_collision
source: backend/tests/test_multi_account.py
line: 199
status: active
tags: [test, function, test]
---

# test_same_provider_message_id_collision

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Two accounts with the same provider_message_id must coexist.

## Location

`backend/tests/test_multi_account.py:199`

## Signature

```python
(tmp_path: Path)
```

## Parameters

- `tmp_path` (`Path`)

## Calls

- [[backend.app.db.repositories.Repository|Repository]] (calls)
- [[backend.app.mail.identity.provider_message_id|provider_message_id]] (calls)
- [[backend.app.mail.identity.scoped_email_id|scoped_email_id]] (calls)
- [[backend.app.mail.providers.gmail.GmailProvider|GmailProvider]] (calls)
- [[backend.app.schemas.SearchFilters|SearchFilters]] (calls)
- [[backend.app.schemas.Task|Task]] (calls)
- `urlsafe_b64encode` (`base64.urlsafe_b64encode`, calls-inferred)

## Reads

- [[table_emails]]

## Side Effects

- SQLite
