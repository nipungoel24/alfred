---
type: function
generated: true
language: python
layer: gmail
module: backend.app.mail.eligibility.MailEligibilityPolicy
qualified_name: backend.app.mail.eligibility.MailEligibilityPolicy.analysis_queue_priority
source: backend/app/mail/eligibility.py
line: 259
status: active
tags: [gmail, function]
---

# analysis_queue_priority

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Processing order for the background analysis queue.

## Location

`backend/app/mail/eligibility.py:259`

## Signature

```python
(cls, label_ids: list[str] | set[str] | None, unread: bool = False, known_thread: bool = False) -> int
```

## Parameters

- `cls`
- `label_ids` (`list[str] | set[str] | None`)
- `unread` (`bool`)
- `known_thread` (`bool`)

## Returns

`int`

## Called By

- [[backend.app.main.analyze_all|analyze_all]]
- [[backend.app.main.sync_account|sync_account]]
- [[backend.tests.test_eligibility.test_gmail_important_is_p0|test_gmail_important_is_p0]]

## Side Effects

- none statically observed
