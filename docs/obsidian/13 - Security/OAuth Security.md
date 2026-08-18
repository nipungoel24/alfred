---
type: security
layer: security
status: active
tags:
  - security
---

# OAuth Security

The OAuth-specific attack surface and its defenses.

## Defenses implemented

- **PKCE S256** — the popup flow has no secret storage; the verifier never leaves backend memory (`OAUTH_STATES`).
- **One-time state** — popped on use; replay of a callback URL fails closed.
- **Minimal scopes** — `userinfo.email` + `gmail.readonly`: no send/modify/settings authority exists to abuse ([[Round 1 Scope]]).
- **Offline + consent** — refresh token guaranteed; token rotation persisted atomically via [[backend.app.db.repositories.Repository.save_credentials]].
- **No tokens in logs** — callback failures log stage + exception type only.

## Residual risks (documented, not solved)

- A malicious local process could race the callback port — mitigated by loopback + one-time state, not by proof of origin.
- Refresh-token theft by same-user malware defeats everything ([[Threat Model]]).

## Related

- [[Google OAuth]]
- [[Token Storage]]
- [[Gmail OAuth Flow]]
