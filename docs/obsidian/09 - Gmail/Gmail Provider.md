---
type: architecture
layer: gmail
status: active
tags:
  - gmail
---

# Gmail Provider

[[backend.app.mail.providers.gmail.GmailProvider|GmailProvider]] — the only class that speaks Gmail's wire protocol.

## Surface

| Method | Purpose |
|---|---|
| `get_auth_url` | PKCE authorization URL (scopes `userinfo.email` + `gmail.readonly`, `access_type=offline`, `prompt=consent`) |
| `exchange_code` | code + verifier → tokens |
| `refresh_tokens` | refresh → access token |
| `get_user_info` | profile email/name |
| `sync_messages` | the sync state machine (initial full / incremental history / load-older pagination) |
| `backfill_messages` | one bounded `-label:INBOX` page per call |
| `refresh_message_labels` | METADATA-only label fetch |
| `_ensure_access_token` | expiry check + rotate + persist |
| `_normalize_message` | Gmail message → [[backend.app.schemas.Email|Email]] (labels, lean `source_metadata`) |
| `_extract_body` / `_clean_html` | MIME decode + HTML strip ([[MIME Parsing]]) |

## Behavioral contracts

- `includeSpamTrash=false` on every `messages.list` — spam/trash never enter the cache through sync.
- Label history events refresh METADATA only — never bodies ([[History Sync]]).
- `messagesDeleted` → `mark_email_excluded`, never `DELETE` ([[Data Ownership]]).
- The typed backfill cursor (state/pages/tokens/estimate) is written after every page ([[backend.app.mail.backfill]]).

## Related

- [[Gmail Overview]]
- [[Gmail Incremental Sync Flow]]
- [[All Mail Backfill Flow]]
