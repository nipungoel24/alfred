---
type: module
generated: true
language: python
layer: backend
qualified_name: backend.app.ai.service
source: backend/app/ai/service.py
status: active
tags: [module, backend]
---

# backend.app.ai.service

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Source

`backend/app/ai/service.py`

## Imports

- `BriefingItem` ← `backend.app.schemas.BriefingItem`
- `Email` ← `backend.app.schemas.Email`
- `EmailAnalysis` ← `backend.app.schemas.EmailAnalysis`
- `InboxBriefing` ← `backend.app.schemas.InboxBriefing`
- `InferenceMetrics` ← `backend.app.ai.ollama_client.InferenceMetrics`
- `OllamaClient` ← `backend.app.ai.ollama_client.OllamaClient`
- `Priority` ← `backend.app.schemas.Priority`
- `json` ← `json`
- `re` ← `re`

## Classes

- [[backend.app.ai.service.AIService|AIService]]

## Functions

- [[backend.app.ai.service.AIService.__init__|__init__]]
- [[backend.app.ai.service.AIService.analyze_email|analyze_email]]
- [[backend.app.ai.service.AIService.draft_reply|draft_reply]]
- [[backend.app.ai.service.AIService.generate_inbox_briefing|generate_inbox_briefing]]
- [[backend.app.ai.service.AIService.health|health]]
- [[backend.app.ai.service.AIService.preload|preload]]
- [[backend.app.ai.service._owner_facing_briefing_summary|_owner_facing_briefing_summary]]
- [[backend.app.ai.service._prepare_body|_prepare_body]]

## Constants

- `ANALYSIS_PROMPT`
- `MAX_BODY_CHARS`
- `PROMPT_VERSION`
- `_BRIEFING_META_LANGUAGE`
- `_ISO_TIMESTAMP`
