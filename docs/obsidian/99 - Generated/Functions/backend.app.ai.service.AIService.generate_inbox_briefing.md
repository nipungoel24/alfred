---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.service.AIService
qualified_name: backend.app.ai.service.AIService.generate_inbox_briefing
source: backend/app/ai/service.py
line: 183
status: active
tags: [ai, function]
---

# generate_inbox_briefing

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Generate an executive inbox briefing from pre-analyzed emails.

## Location

`backend/app/ai/service.py:183`

## Signature

```python
(self, emails: list[Email]) -> InboxBriefing
```

## Parameters

- `self`
- `emails` (`list[Email]`)

## Returns

`InboxBriefing`

## Calls

- [[backend.app.schemas.BriefingItem|BriefingItem]] (calls)
- `model_json_schema` (`backend.app.schemas.InboxBriefing.model_json_schema`, calls-inferred)
- `model_validate_json` (`backend.app.schemas.InboxBriefing.model_validate_json`, calls-inferred)
- `dumps` (`json.dumps`, calls-inferred)

## Side Effects

- async I/O
