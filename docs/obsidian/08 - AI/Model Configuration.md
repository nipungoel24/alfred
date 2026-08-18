---
type: architecture
layer: ai
status: active
tags:
  - ai
---

# Model Configuration

Alfred pins a single model and treats it as a contract.

## Settings ([[backend.app.config.Settings]])

- `OLLAMA_MODEL` — default `qwen3:4b` (see [[ADR-005 - qwen3 4b]]).
- `OLLAMA_BASE_URL` — default `http://127.0.0.1:11434`.

## Generation knobs

- `temperature: 0.0` for analysis and briefing (deterministic structured extraction), `0.7` for draft generation (natural prose).
- `keep_alive: 30m` — model stays warm between bursts; startup preload warms it once.
- `think: false` — disables reasoning-token output for speed; leak-stripping is a belt-and-braces defense.
- Body truncation at 2000 chars (~500–700 tokens) keeps prompts far inside the 32K context ([[Prompt Architecture]]).

## Cache coupling

Cached analyses are keyed by `content_hash + model_name + schema_version` — switching `OLLAMA_MODEL` naturally invalidates nothing old, but old caches won't be reused for the new model (each model has its own cache lines). See [[AI Caching]].

## Related

- [[Environment Variables]]
- [[Ollama Integration]]
- [[AI Performance]]
