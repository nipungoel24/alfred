---
type: adr
layer: meta
status: active
tags:
  - architecture
  - security
---

# ADR-013 - DPAPI Token Storage

## Status

Accepted

## Context

OAuth tokens in a plaintext SQLite file would be readable by any local process.

## Decision

Encrypt refresh/access tokens with Windows **DPAPI** ([[backend.app.db.secure_store]]) before persistence; decrypt only per call; rotate on expiry.

## Alternatives Considered

- User passphrase keyring — friction and recovery complexity for Round 1.
- Plaintext — unacceptable.

## Why

DPAPI ties ciphertext to the Windows user account with zero key management; appropriate for a single-user desktop trust model.

## Consequences

- Non-Windows dev environments fall back to base64 (documented, weaker — the product targets Windows).
- Same-user malware remains an accepted residual ([[Threat Model]]).

## Related Code

- [[backend.app.db.secure_store.encrypt_token|encrypt_token]]
- [[credentials]]

## Related Documentation

- [[DPAPI]]
- [[Token Storage]]
