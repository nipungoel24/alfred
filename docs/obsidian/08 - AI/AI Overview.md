---
type: architecture
layer: ai
status: active
tags:
  - ai
  - architecture
---

# AI Overview

Three prompts, one local model, zero cloud. Everything the AI does is described in [[AI Architecture]]; this note catalogs the deep dives.

## Components

- [[backend.app.ai.ollama_client.OllamaClient|OllamaClient]] — transport: `/api/generate`, `stream=false`, `think=false`, structured `format`, timings, error taxonomy ([[backend.app.ai.ollama_client.OllamaUnavailable|OllamaUnavailable]]/[[backend.app.ai.ollama_client.OllamaTimeout|OllamaTimeout]]/[[backend.app.ai.ollama_client.OllamaInvalidResponse|OllamaInvalidResponse]]/[[backend.app.ai.ollama_client.OllamaModelMissing|OllamaModelMissing]]).
- [[backend.app.ai.service.AIService|AIService]] — the three prompts + body sanitization + local count overrides.
- [[backend.app.schemas]] — the schemas the model must fill ([[Analysis Schema]]).

## Deep dives

- [[Ollama Integration]]
- [[Model Configuration]]
- [[Structured Output]]
- [[Prompt Architecture]]
- [[Analysis Schema]]
- [[Task Intelligence]]
- [[Prompt Injection Defense]]
- [[AI Caching]]
- [[AI Performance]]
- [[AI Failure Handling]]

## Related flows

- [[Email Analysis Flow]]
- [[Briefing Generation Flow]]
- [[Draft Generation Flow]]
