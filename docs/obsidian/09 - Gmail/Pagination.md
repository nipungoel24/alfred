---
type: architecture
layer: gmail
status: active
tags:
  - gmail
---

# Pagination

Two independent pagination loops, both cursor-persisted in [[accounts]].

## Inbox listing pagination

- `messages.list?q=label:INBOX&maxResults=50&pageToken=…` — used by the full-sync/recovery path and the "load older" feature.
- `next_page_token` persists in the cursor and survives restart; loading older pages never disturbs `history_id`.

## All Mail backfill pagination

- `messages.list?q=-label:INBOX&maxResults=40&pageToken=…` — one page per worker run, rate-limited (`not_before +2.5s`), priority below analysis.
- `backfill_page_token` persists independently; completion is typed (`backfill_state=complete`), not inferred ([[All Mail Backfill Flow]]).

## Shared invariants

- `includeSpamTrash=false` on every listing call.
- Page results are idempotent: cached ids are skipped (labels refreshed), so re-running a page is free.
- Cursors are written only after the page finishes → crash-safe resume.

## Related

- [[History Sync]]
- [[All Mail Backfill Flow]]
- [[Gmail Incremental Sync Flow]]
