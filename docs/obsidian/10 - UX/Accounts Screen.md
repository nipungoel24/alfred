---
type: architecture
layer: frontend
status: active
tags:
  - frontend
---

# Accounts Screen

[[frontend.src.features.accounts.AccountsPage.AccountsPage|AccountsPage]] — provider lifecycle.

- Empty state → *Connect Gmail* → popup OAuth ([[Gmail OAuth Flow]]) → `postMessage` refresh.
- Account card: provider icon, display name/email, connection status dot, last-sync timestamp.
- Actions: **Sync Now** ([[POST --api-accounts-{account_id}-sync]]), **Disconnect** ([[DELETE --api-accounts-{account_id}]]).
- Errors surface as scoped banners.

## Related

- [[API Map]]
- [[Gmail Errors]]
