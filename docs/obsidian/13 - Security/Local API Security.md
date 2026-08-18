---
type: security
layer: security
status: active
tags:
  - security
---

# Local API Security

The FastAPI surface is product surface, so it is locked down by construction.

- **Bind**: `127.0.0.1` only (`ALFRED_HOST` default) — not routable from other machines.
- **CORS**: `localhost:5173`, `127.0.0.1:5173`, `tauri://localhost` — the browser origin set that legitimately exists.
- **CSP (Tauri)**: `connect-src` restricted to the local backend ([[Native Security]]).
- **No auth token on the API itself** — protection relies on the loopback boundary; any local process could call it. Accepted residual ([[Threat Model]]); the API has no secret-returning endpoints (accounts/cursors/emails are the data the local user already owns).

## Related

- [[Trust Boundaries]]
- [[API Overview]]
- [[Threat Model]]
