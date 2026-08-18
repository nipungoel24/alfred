---
type: function
generated: true
language: python
layer: test
module: backend.tests.test_allmail
qualified_name: backend.tests.test_allmail.test_archived_excluded_from_intelligence
source: backend/tests/test_allmail.py
line: 148
status: active
tags: [test, function, test]
---

# test_archived_excluded_from_intelligence

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Purpose inferred from usage: `test_archived_excluded_from_intelligence` in `backend/tests/test_allmail.py`.

## Location

`backend/tests/test_allmail.py:148`

## Signature

```python
(repo)
```

## Parameters

- `repo`

## Calls

- [[backend.app.db.repositories.Repository.eligible_emails_without_analysis|eligible_emails_without_analysis]] (calls)
- [[backend.app.db.repositories.Repository.emails_filtered|emails_filtered]] (calls)
- [[backend.app.db.repositories.Repository.upsert_email|upsert_email]] (calls)
- [[backend.app.mail.eligibility.MailEligibilityPolicy.should_include_in_briefing|should_include_in_briefing]] (calls)
- [[backend.app.mail.eligibility.MailEligibilityPolicy.should_schedule_analysis|should_schedule_analysis]] (calls)

## Reads

- [[table_email_analysis]]
- [[table_emails]]

## Writes

- [[table_emails]]

## Side Effects

- SQLite
