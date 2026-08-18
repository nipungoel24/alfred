---
type: adr
layer: meta
status: active
tags:
  - architecture
  - frontend
---

# ADR-011 - SSE Progress

## Status

Accepted

## Context

The UI needed live progress for background analysis without polling endpoints into oblivion.

## Decision

Server-Sent Events: one in-process hub broadcasts worker events; the frontend's single progress component listens and **debounces** query invalidation (1s) rather than refetching per event.

## Why

SSE is a hint layer, not the data source — drops are harmless because React Query's normal cadence redis covers reality ([[SSE Progress Flow]]).

## Consequences

- Heartbeats (15s) keep proxies from closing idle streams.
- One EventSource for the whole app keeps the surface small.

## Related Code

- [[GET --api-analysis-progress]]
- [[frontend.src.components.ui.AnalysisProgress.AnalysisProgress|AnalysisProgress]]

## Related Documentation

- [[SSE Progress Flow]]
- [[Frontend Data Fetch Flow]]
