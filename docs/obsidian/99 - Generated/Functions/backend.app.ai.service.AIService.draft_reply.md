---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.service.AIService
qualified_name: backend.app.ai.service.AIService.draft_reply
source: backend/app/ai/service.py
line: 147
status: active
tags: [ai, function]
---

# draft_reply

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Generate a reply draft using bounded thread context.

## Location

`backend/app/ai/service.py:147`

## Signature

```python
(self, email: Email, thread_emails: list[Email] | None = None) -> str
```

## Parameters

- `self`
- `email` (`Email`)
- `thread_emails` (`list[Email] | None`)

## Returns

`str`

## Calls

- `dumps` (`json.dumps`, calls-inferred)

## Side Effects

- async I/O
