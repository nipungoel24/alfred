---
type: architecture
layer: gmail
status: active
tags:
  - gmail
---

# Gmail Errors

Every Gmail failure mode Alfred handles, and the policy per mode.

| Condition | Detection | Handling |
|---|---|---|
| Access token expired | `expires_at` check | silent refresh + persist ([[Token Storage]]) |
| Refresh rejected | OAuth token endpoint error | account `connection_status=error`, sync raises |
| historyId expired (410/404) | history call status | full-sync recovery ([[History Sync]]) |
| Individual message fetch fails | per-message try/except | skipped for that message, page continues |
| Rate limits / 5xx during backfill | httpx error | retryable job + exponential backoff (30s→5m), then `failed` state |
| 401/403 during backfill | httpx status | terminal `failed` state (no point retrying) |
| Gmail API down during sync | exception | HTTP 500 to caller; state unchanged (cursor intact) |

## Frontend surface

- Sync errors appear as scoped banners on [[frontend.src.features.accounts.AccountsPage.AccountsPage|AccountsPage]].
- Backfill `last_error` is sanitized into the status payload (code + short message) shown near the All Mail count.
- Connectivity status in the rail/header reflects account `connection_status`.

## Related

- [[History Sync]]
- [[All Mail Backfill Flow]]
- [[backend.app.mail.providers.gmail.GmailProvider|GmailProvider]]
