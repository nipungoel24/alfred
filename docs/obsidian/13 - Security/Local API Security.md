---
type: security
layer: security
status: active
tags:
  - security
---

# Local API Security

The FastAPI surface is product surface, so it is locked down by construction — and now authenticated.

- **Bind**: `127.0.0.1` only — not routable from other machines.
- **Runtime authentication** (production): per-launch high-entropy token enforced by middleware on `/api/*` and `/health` (header `X-Alfred-Token`; `?token=` query only for EventSource, which cannot send headers). See [[ADR-015 - Desktop Session Authentication]].
- **Dynamic port**: Tauri picks a free loopback port per launch — Alfred never assumes 8765 belongs to it, and never talks to a foreign process squatting the port.
- **CORS**: `localhost:5173`, `127.0.0.1:5173`, `tauri://localhost` ([[Native Security]] CSP complements this).
- **Graceful shutdown endpoint**: `/api/shutdown` is token-protected like everything else.

## Residual risk (documented)

The token lives in the environment of the sidecar process on the same machine; same-user malware can read it — accepted in the local trust model ([[Threat Model]]). The token is per-launch and non-persistent, so a stolen token dies with the session.

## Related

- [[Trust Boundaries]]
- [[API Overview]]
- [[Threat Model]]
