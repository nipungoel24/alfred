---
type: architecture
layer: gmail
status: active
tags:
  - gmail
  - security
---

# Token Storage

Where OAuth material lives, in what form, and how it moves.

## At rest

| Material | Storage | Protection |
|---|---|---|
| Refresh token | `encrypted_refresh_token` in [[credentials]] (BLOB) | DPAPI ciphertext |
| Access token | `encrypted_access_token` in [[credentials]] (BLOB) | DPAPI ciphertext |
| Expiry | `expires_at` in [[credentials]] (ISO text) | — |

## In memory

- `main.py` decrypts on demand for sync/backfill calls (`decrypt_token`) and discards after the call.
- `OAUTH_STATES` holds PKCE verifiers in a dict — process memory only.

## Rotation

[[backend.app.mail.providers.gmail.GmailProvider._ensure_access_token]] checks `expires_at` before every Gmail call; if expired, it refreshes, re-encrypts, and persists the new pair before proceeding. This is the single write path for credentials after account creation.

## What DPAPI is and isn't

DPAPI encrypts with a key tied to the Windows user account: another *process* on the same machine cannot easily read the blobs, and file copies across machines are useless. It is **not** end-to-end encryption and does not protect against malware running as the same user — see [[DPAPI]] and [[Threat Model]].

## Related

- [[credentials]]
- [[backend.app.db.secure_store]]
- [[OAuth Security]]
