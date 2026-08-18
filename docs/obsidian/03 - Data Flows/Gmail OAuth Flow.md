---
type: data-flow
layer: gmail
status: active
tags:
  - system
  - gmail
  - security
  - critical-path
---

# Gmail OAuth Flow

How Alfred obtains and keeps Gmail credentials, end to end.

```mermaid
sequenceDiagram
    participant U as User (AccountsPage)
    participant FE as Frontend
    participant BE as FastAPI
    participant B as System Browser
    participant G as Google
    participant D as DPAPI/SQLite

    U->>FE: Click "Connect Gmail"
    FE->>BE: POST /api/accounts/gmail/connect
    BE->>BE: generate PKCE verifier+challenge, state
    BE-->>FE: { url }
    FE->>B: window.open(auth url)
    B->>G: accounts.google.com (scopes: gmail.readonly, userinfo.email)
    U->>G: consent
    G->>B: redirect with code+state
    B->>BE: GET /api/accounts/gmail/callback?code&state
    BE->>BE: validate state (OAUTH_STATES)
    BE->>G: POST oauth2.googleapis.com/token (code + verifier)
    G-->>BE: access_token, refresh_token
    BE->>G: userinfo (email, name)
    BE->>D: DPAPI-encrypt tokens → credentials table
    BE->>BE: save account row (sync_cursor=null)
    BE-->>B: success HTML page → postMessage to opener
    FE->>FE: invalidate accounts query
```

## Key mechanics

- **PKCE (S256)** — the popup flow can't keep a client secret safe, so proof-key exchange protects the code: `generate_pkce_pair` in [[backend.app.main]].
- **State validation** — one-time state entries in `OAUTH_STATES` (in-memory); consumed on callback ([[OAuth Security]]).
- **Offline access** — `access_type=offline` + `prompt=consent` so a refresh token is always issued.
- **Scopes** — exactly `userinfo.email` + `gmail.readonly`; sending is impossible by scope design ([[Round 1 Scope]]).
- **Storage** — [[backend.app.db.secure_store.encrypt_token]] → DPAPI ciphertext in [[credentials]]; account id is `gmail_<email>`.

## Handlers

- [[POST --api-accounts-gmail-connect]] → [[POST --api-accounts-gmail-connect|connect_gmail]]
- [[GET --api-accounts-gmail-callback]] → [[GET --api-accounts-gmail-callback|gmail_callback]]
- Provider primitives: [[backend.app.mail.providers.gmail.GmailProvider.get_auth_url]], `exchange_code`, `refresh_tokens`

## Failure modes

- Denied consent → error page ([[backend.app.main._oauth_callback_page|_oauth_callback_page]]), status 400.
- Unknown/expired state → warn log, error page.
- Token exchange failure → stage-tagged warning log; no account row persisted on failure.

## Related

- [[Google OAuth]]
- [[Token Storage]]
- [[OAuth Security]]
- [[backend.tests.test_gmail_mock.test_gmail_oauth_url_generation]]
