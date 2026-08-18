---
type: adr
layer: meta
status: active
tags:
  - architecture
  - backend
---

# ADR-002 - FastAPI Backend

## Status

Accepted

## Context

The legacy prototype was a Streamlit + LangGraph + Groq app (`src/`, `config/`) with session-only state and eager cloud inference. Alfred needed a persistent, local, async API.

## Decision

A **FastAPI** application owns: OAuth callbacks, Gmail sync, the AI pipeline, SQLite, and SSE. It runs as a sidecar under Tauri and standalone during development.

## Alternatives Considered

- Node/Express backend — Python wins on Pydantic schemas shared with the AI structured-output contract.
- Rust service — higher build cost for no Round 1 need.

## Why

Pydantic schemas are the single contract for API, storage, and the model's `format` parameter ([[Structured Output]]). Async fits Gmail/Ollama I/O.

## Consequences

- The backend is a second process to package ([[Sidecar Architecture]]).
- The legacy `src/` prototype remains in-tree as historical code, not runtime.

## Related Code

- [[backend.app.main]]
- [[backend.app.schemas]]

## Related Documentation

- [[Backend Architecture]]
- [[Sidecar Architecture]]
