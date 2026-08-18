---
type: architecture
layer: gmail
status: active
tags:
  - gmail
  - security
---

# Google OAuth

The authorization wiring between Alfred and Google.

## Choice: popup + PKCE

Alfred is a desktop app; a web-server secret can't be hidden in it. So:

- **PKCE S256** (`generate_pkce_pair` in [[backend.app.main]]) — the code challenge travels in the URL, the verifier stays in backend memory (`OAUTH_STATES`).
- **State** — one-time random token binding the popup to the initiating backend instance.
- **Offline + consent** — refresh tokens are mandatory for a sync product that runs unattended.

## Callback hardening

- State must exist in `OAUTH_STATES` and is consumed (one-time) on use.
- `error` param → denied page; missing code/state → failed page; failures are stage-logged without secrets ([[Gmail OAuth Flow]]).
- The callback page signals the opener via `postMessage('auth_success')` so the UI can refresh accounts.

## Scope discipline

Exactly `userinfo.email` + `gmail.readonly`. No `send`, no `labels.modify`, no `settings` — the credential itself makes destructive Gmail actions impossible ([[Round 1 Scope]], [[OAuth Security]]).

## Related

- [[Gmail OAuth Flow]]
- [[Token Storage]]
- [[OAuth Security]]
