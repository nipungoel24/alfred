---
type: architecture
layer: gmail
status: active
tags:
  - gmail
  - security
---

# DPAPI

Windows Data Protection API — the encryption boundary behind Alfred's token storage.

## Implementation ([[backend.app.db.secure_store]])

- `_win_encrypt` — `CryptProtectData` via ctypes; `_win_decrypt` — `CryptUnprotectData`; both free the returned `DATA_BLOB` with `LocalFree`.
- `encrypt_token` / `decrypt_token` — platform dispatch: DPAPI on `win32`, base64 fallback elsewhere (the fallback exists for non-Windows dev environments and is documented as weaker — the product targets Windows).
- Failures in DPAPI calls fall through to the base64 path — chosen so a broken Windows profile degrades gracefully rather than locking users out; documented tradeoff.

## Security properties

- Key material is derived from the Windows user profile — no secret to store or rotate.
- Binds ciphertext to the machine+user: copying `alfred.sqlite3` to another machine yields undecryptable tokens.
- Protects at rest only; any code running *as the same user* can decrypt — hence the local-API and threat-model notes ([[Local API Security]], [[Threat Model]]).

## Related

- [[Token Storage]]
- [[credentials]]
- [[Native Security]]
