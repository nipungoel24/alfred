---
type: security
layer: security
status: active
tags:
  - security
---

# Token Security

Token lifecycle security: acquire → store → use → rotate → revoke.

- **Acquire**: PKCE + state + minimal scope ([[OAuth Security]]).
- **Store**: DPAPI BLOBs in [[credentials]]; plaintext appears only transiently in backend memory during calls ([[Token Storage]]).
- **Use**: decrypted per call; `_ensure_access_token` rotates before expiry; refresh errors mark the account `error` rather than crash-looping.
- **Rotate**: every expiry → new access token re-encrypted; refresh token re-encrypted alongside.
- **Revoke**: user disconnect deletes the account row (cascades credentials) — server-side revocation is Google-side and out of scope for Round 1.

## Related

- [[DPAPI]]
- [[credentials]]
- [[OAuth Security]]
