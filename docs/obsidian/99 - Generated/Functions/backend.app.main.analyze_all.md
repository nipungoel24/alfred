---
type: function
generated: true
language: python
layer: backend
module: backend.app.main
qualified_name: backend.app.main.analyze_all
source: backend/app/main.py
line: 886
status: active
tags: [backend, function, endpoint]
---

# analyze_all

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Enqueue all eligible unanalyzed emails for background analysis.

## Route

`POST /api/emails/analyze`

## Location

`backend/app/main.py:886`

## Signature

```python
()
```

## Calls

- [[backend.app.mail.eligibility.MailEligibilityPolicy.analysis_queue_priority|analysis_queue_priority]] (calls)
- [[backend.app.mail.eligibility.MailEligibilityPolicy.is_unread|is_unread]] (calls)
- [[backend.app.mail.eligibility.MailEligibilityPolicy.should_schedule_analysis|should_schedule_analysis]] (calls)
- [[backend.app.mail.fingerprint.content_fingerprint|content_fingerprint]] (calls)

## Side Effects

- async I/O
