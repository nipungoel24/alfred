---
type: adr
layer: meta
status: active
tags:
  - architecture
  - ai
---

# ADR-004 - Ollama Local AI

## Status

Accepted

## Context

The legacy prototype used cloud inference (Groq). Alfred's product promise is privacy ([[Privacy Model]]).

## Decision

All inference runs through **Ollama** on loopback (`127.0.0.1:11434`). No cloud model calls exist anywhere.

## Alternatives Considered

- Direct llama.cpp embedding — Ollama's HTTP API + model registry is the pragmatic layer.
- Cloud models with "privacy modes" — rejected on principle, not performance.

## Why

Local inference makes the privacy claim real: mail text only ever reaches a process the user runs.

## Consequences

- Model availability is a user dependency ([[AI Failure Handling]]).
- Hardware bounds the model size ([[ADR-005 - qwen3 4b]]).

## Related Code

- [[backend.app.ai.ollama_client.OllamaClient|OllamaClient]]

## Related Documentation

- [[AI Architecture]]
- [[Ollama Integration]]
