---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_eligibility
qualified_name: backend.tests.test_eligibility.test_spam_transition_hides_from_projections
source: backend/tests/test_eligibility.py
line: 215
status: active
tags: [test, function, test]
---

# test_spam_transition_hides_from_projections

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_spam_transition_hides_from_projections` in `backend/tests/test_eligibility.py`.

## Location

`backend/tests/test_eligibility.py:215`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.email_counts|email_counts]] (calls)
- [[backend.app.db.repositories.Repository.email_exists|email_exists]] (calls)
- [[backend.app.db.repositories.Repository.emails_filtered|emails_filtered]] (calls)
- [[backend.app.db.repositories.Repository.update_email_labels|update_email_labels]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)

## Reads

- [[table_emails]]

## Writes

- [[table_emails]]

## Side Effects

- SQLite
