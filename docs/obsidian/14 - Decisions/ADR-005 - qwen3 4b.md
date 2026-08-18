---
type: adr
layer: meta
status: active
tags:
  - architecture
  - ai
---

# ADR-005 - qwen3 4b

## Status

Accepted

## Context

The model must run on a consumer Windows machine and support structured output.

## Decision

Default model is **qwen3:4b** (`OLLAMA_MODEL`).

## Alternatives Considered

- Larger models — better quality, too slow/heavy for background inbox work on typical hardware.
- Other small models — qwen3 won on structured-output reliability in the golden corpus work.

## Why

4B keeps inference interactive on CPU-class hardware while `format` support makes the JSON contract dependable ([[Structured Output]]).

## Consequences

- Prompts are engineered for a small model: hard rules, local count recomputation, meta-language guards ([[Prompt Architecture]], [[Briefing Generation Flow]]).

## Related Code

- [[backend.app.config.Settings]]
- [[backend.app.ai.service]]

## Related Documentation

- [[Model Configuration]]
- [[AI Performance]]
