---
type: adr
layer: meta
status: active
tags:
  - architecture
  - ai
---

# ADR-008 - Separate Action Candidates From Tasks

## Status

Accepted

## Context

The model's raw `action_items` are noisy: marketing CTAs, third-party owners, phishing lures. Promoting them directly to tasks polluted the task list and eroded trust.

## Decision

Two layers: **action candidates** live inside [[email_analysis]]; **tasks** ([[tasks]]) are a validated projection created only by [[backend.app.services.task_derivation.derive_tasks]] with length/noise/ownership/category gates and fingerprints.

## Alternatives Considered

- Prompt-only filtering — unreliable on a small model.
- Everything is a task, user sorts it out — the exact failure this fixes.

## Why

Deterministic gates are testable ([[backend.tests.test_task_derivation]]); the model stays an analysis engine, not a task authority.

## Consequences

- Derivation rules can evolve without re-running the LLM ([[ADR-009 - Versioned Task Derivation]]).
- The analysis remains honest even when the task projection is strict.

## Related Code

- [[backend.app.services.task_derivation]]
- [[backend.app.schemas.ActionItem|ActionItem]]

## Related Documentation

- [[Task Derivation Flow]]
- [[Task Intelligence]]
