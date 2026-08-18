---
type: function
generated: true
language: python
layer: ai
module: backend.app.ai.service.AIService
qualified_name: backend.app.ai.service.AIService.analyze_email
source: backend/app/ai/service.py
line: 122
status: active
tags: [ai, function, critical-path]
---

# analyze_email

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Purpose

Analyze a single email and return structured analysis with metrics.

## Location

`backend/app/ai/service.py:122`

## Signature

```python
(self, email: Email) -> tuple[EmailAnalysis, InferenceMetrics]
```

## Parameters

- `self`
- `email` (`Email`)

## Returns

`tuple[EmailAnalysis, InferenceMetrics]`

## Calls

- `model_json_schema` (`backend.app.schemas.EmailAnalysis.model_json_schema`, calls-inferred)
- `model_validate_json` (`backend.app.schemas.EmailAnalysis.model_validate_json`, calls-inferred)
- `dumps` (`json.dumps`, calls-inferred)

## Side Effects

- async I/O
