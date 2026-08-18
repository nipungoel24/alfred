---
type: adr
layer: meta
status: active
tags:
  - architecture
  - frontend
---

# ADR-010 - React Query

## Status

Accepted

## Context

Hand-rolled fetching led to duplicated requests, stale UI after sync/analysis, and no cache discipline.

## Decision

All server state flows through **TanStack Query**: keyed queries (`['emails', {scope, category, …}]`), stale-while-revalidate, targeted invalidation on mutations and SSE events.

## Why

Query keys encode the view so tab switches hit cache; invalidation lists are explicit per mutation — the request-storm bug class disappears by construction ([[SSE Progress Flow]]).

## Consequences

- The frontend holds a bounded window of data; virtualization + server-side filtering do the rest ([[ADR-012 - Inbox Virtualization]]).
- Backfill progress is observed via refetch intervals, not polling ownership ([[All Mail Backfill Flow]]).

## Related Code

- [[frontend.src.api.emails]]
- [[frontend.src.mail.MailWorkspace.MailWorkspace|MailWorkspace]]

## Related Documentation

- [[Frontend Data Fetch Flow]]
- [[Frontend Architecture]]
