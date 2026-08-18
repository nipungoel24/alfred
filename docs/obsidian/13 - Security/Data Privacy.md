---
type: security
layer: security
status: active
tags:
  - security
---

# Data Privacy

What Alfred stores, where, and what that means for the user.

- Everything lives in `%LOCALAPPDATA%/Alfred/`: SQLite (mail mirror, analyses, tasks, cursors) + logs.
- OAuth tokens are DPAPI ciphertext ([[Token Storage]]); mail content is plaintext JSON protected by the OS account ([[Privacy Model]]).
- No telemetry exists in the codebase; the only outbound traffic is Gmail API reads and loopback Ollama calls.
- Deletion: disconnecting the account removes its rows; there is no remote wipe (Google-side data is untouched — read-only scope).

## Related

- [[Privacy Model]]
- [[Threat Model]]
- [[Data Ownership]]
