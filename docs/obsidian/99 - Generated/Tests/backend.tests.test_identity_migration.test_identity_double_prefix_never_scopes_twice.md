---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_identity_migration
qualified_name: backend.tests.test_identity_migration.test_identity_double_prefix_never_scopes_twice
source: backend/tests/test_identity_migration.py
line: 43
status: active
tags: [test, function, test]
---

# test_identity_double_prefix_never_scopes_twice

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

An already-scoped id round-trips, so re-scoping is impossible.

## Location

`backend/tests/test_identity_migration.py:43`

## Signature

```python
()
```

## Calls

- [[backend.app.mail.identity.parse_email_id|parse_email_id]] (calls)
- [[backend.app.mail.identity.scoped_email_id|scoped_email_id]] (calls)

## Side Effects

- none statically observed
