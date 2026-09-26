---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_identity_migration
qualified_name: backend.tests.test_identity_migration.test_identity_underscore_email
source: backend/tests/test_identity_migration.py
line: 29
status: active
tags: [test, function, test]
---

# test_identity_underscore_email

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Account local-parts may contain underscores — parsing must survive.

## Location

`backend/tests/test_identity_migration.py:29`

## Signature

```python
()
```

## Calls

- [[backend.app.mail.identity.is_scoped_for|is_scoped_for]] (calls)
- [[backend.app.mail.identity.parse_email_id|parse_email_id]] (calls)
- [[backend.app.mail.identity.scoped_email_id|scoped_email_id]] (calls)

## Side Effects

- none statically observed
