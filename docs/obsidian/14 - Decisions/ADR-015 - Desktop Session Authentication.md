---
type: adr
layer: meta
status: active
tags:
  - architecture
  - security
---

# ADR-015 - Desktop Session Authentication

## Status

Accepted

## Context

The local FastAPI binds 127.0.0.1, but any local process (or a malicious web page targeting localhost) could otherwise issue privileged Alfred API requests. A fixed port number also risks talking to a foreign service that grabbed the port first.

## Decision

Tauri generates a **high-entropy runtime token per launch** and a **dynamic free loopback port**, passes both to the sidecar as environment (`ALFRED_RUNTIME_TOKEN`, `ALFRED_PORT`), and exposes them to the webview only through the controlled `backend_info` command. The backend middleware rejects any `/api/*` (and `/health`) request without the matching token. The token is never persisted, never logged, and never leaves the two local processes. EventSource (which cannot set headers) uses a `?token=` query fallback.

## Alternatives Considered

- OAuth-style login for the local API — absurd for a loopback process pair.
- Fixed port + trust-by-default — rejected: port collision means a wrong service could answer; the token makes identity explicit.

## Why

Port coordination + secret together mean Alfred never talks to a foreign process, and foreign processes cannot drive Alfred. Development mode stays frictionless: no `ALFRED_RUNTIME_TOKEN` → no enforcement.

## Consequences

- `/health` and `/api/shutdown` are token-protected in production mode.
- The runtime token is visible in the sidecar environment of the same machine (same trust level) — accepted per the local threat model ([[Threat Model]]).

## Related Code

- `runtime_token_middleware` in [[backend.app.main]]
- `backend_info` / `retry_backend` in `desktop/src-tauri/src/main.rs`
- [[frontend.src.api.client]]

## Related Documentation

- [[Local API Security]]
- [[Desktop Architecture]]
- [[ADR-016 - Tauri-Owned Sidecar Lifecycle]]
