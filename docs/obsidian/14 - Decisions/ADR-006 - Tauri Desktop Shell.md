---
type: adr
layer: meta
status: active
tags:
  - architecture
  - desktop
---

# ADR-006 - Tauri Desktop Shell

## Status

Accepted

## Context

Alfred is a desktop product for Windows; a browser tab isn't the product shape.

## Decision

Package with **Tauri 2**: the React frontend in a system webview, the FastAPI backend as a compiled sidecar.

## Alternatives Considered

- Electron — heavier runtime, less aligned with the lean aesthetic.
- Web-only — rejected; desktop presence (OAuth popup, tray, startup) matters.

## Why

Tauri's sidecar model fits the Python backend perfectly and keeps the footprint small.

## Consequences

- CSP/capability discipline is mandatory ([[Native Security]]).
- Packaging QA remains an open item ([[Project Status]]).

## Related Code

- `desktop/src-tauri/src/main.rs`
- `desktop/src-tauri/tauri.conf.json`

## Related Documentation

- [[Desktop Architecture]]
- [[Sidecar Architecture]]
