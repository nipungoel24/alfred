---
type: adr
layer: meta
status: active
tags:
  - architecture
  - frontend
---

# ADR-012 - Inbox Virtualization

## Status

Accepted

## Context

A real mailbox can hold thousands of messages; rendering them all destroys the DOM.

## Decision

`@tanstack/react-virtual` with dynamic row measurement inside the message list; list endpoints stay paginated (`limit`/`offset`) and filtering stays server-side.

## Why

The client only ever renders ~a screenful of rows; category/scope/search are SQL parameters, so memory and network stay proportional to what's visible ([[Frontend Data Fetch Flow]]).

## Consequences

- Skeletons and empty states must live inside the virtualized pane (layout stability).
- Rows keep fixed semantic height targets for smooth measurement.

## Related Code

- [[frontend.src.mail.MessageList.MessageList|MessageList]]
- [[GET --api-emails]]

## Related Documentation

- [[Mail Workspace Screen]]
- [[ADR-010 - React Query]]
