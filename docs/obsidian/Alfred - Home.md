---
type: home
layer: meta
status: active
tags:
  - system
  - architecture
---

# Alfred

## What is Alfred?

Alfred is a local-first smart inbox for Windows: it reads a single Gmail mailbox, keeps a private SQLite mirror of the messages that matter, and runs a small local AI (Ollama + qwen3:4b) over them to produce executive-level intelligence — priorities, summaries, replies-needed, derived tasks, deadlines, and a daily briefing. The UI is a Mattered-style three-pane mail workspace wrapped in a Tauri desktop shell.

The name Alfred is a deliberate nod: a quiet butler for your inbox.

## Current Scope

- Gmail only ([[ADR-001 - Gmail Only Round 1]]), read-only (`gmail.readonly`).
- Local AI via Ollama ([[ADR-004 - Ollama Local AI]]), model qwen3:4b ([[ADR-005 - qwen3 4b]]).
- SQLite storage ([[ADR-003 - SQLite Storage]]), FastAPI sidecar backend ([[ADR-002 - FastAPI Backend]]).
- All analysis stays on this machine — see [[Privacy Model]].
- No sending, no cloud AI, no IMAP/Outlook (Round 1).

## System Map

- [[System Architecture]] — the whole picture in one diagram.
- [[Product Vision]] — why Alfred exists.
- [[Round 1 Scope]] — exactly what is and isn't in scope.

## Explore by Area

- Backend — [[Backend Architecture]], [[Backend Overview]], [[Backend Code Map]]
- Frontend — [[Frontend Architecture]], [[Frontend Overview]], [[Frontend Code Map]]
- Gmail — [[Gmail Architecture]], [[Gmail Overview]]
- AI — [[AI Architecture]], [[AI Overview]]
- Database — [[Database Architecture]], [[Database Overview]]
- Security — [[Security Architecture]], [[Threat Model]]
- Desktop — [[Desktop Architecture]], [[Tauri Overview]]
- Testing — [[Testing Strategy]], [[Test Coverage Map]]

## Critical Data Flows

- [[Gmail OAuth Flow]]
- [[Gmail Incremental Sync Flow]]
- [[Email Analysis Flow]]
- [[Task Derivation Flow]]
- [[SSE Progress Flow]]
- [[Application Startup Flow]]
- [[All Mail Backfill Flow]]

## Code Maps

- [[Backend Code Map]]
- [[Frontend Code Map]]
- [[Dependency Map]]
- [[Entry Points]]
- [[Critical Execution Paths]]

## Decisions

- [[ADR Index]] — all Architecture Decision Records.

## Development

- [[Development Setup]]
- [[Running Alfred]]
- [[Environment Variables]]
- [[How to Navigate This Vault]]

## Engineering Journal

- [[Engineering Journal]] (17 - Engineering Journal) — how the system evolved.
