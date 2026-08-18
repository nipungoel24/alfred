---
type: architecture
layer: test
status: active
tags:
  - test
  - ai
---

# Golden Email Corpus

Fixed representative emails (`backend/tests/inbox.csv` + fixtures in [[backend.tests.test_golden_corpus]]) used to verify the AI contract deterministically.

## Why

Ollama is slow and non-deterministic; running it in CI for every test would be flaky. The corpus instead validates everything *around* the model: prompt construction, schema validation, error handling, and derivation gates — with the model mocked ([[backend.tests.test_ollama_mock]]).

## What it covers

- Structured-output parse/validate paths ([[Structured Output]]).
- Noise patterns in task derivation ("click here", credential lures…) — [[Task Intelligence]].
- Deadline extraction confidence rules ([[Deadline Extraction Flow]]).
- Priority score bands ([[Analysis Schema]]).

## Real-model verification

The real mailbox itself serves as the live acceptance corpus — no reset, counts-only reporting ([[Gmail E2E Testing]]).

## Related

- [[Testing Strategy]]
- [[AI Testing]]
