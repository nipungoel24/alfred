---
type: architecture
layer: gmail
status: active
tags:
  - gmail
---

# History Sync

The `historyId`-based incremental protocol that keeps the inbox fresh without re-listing it.

## Protocol

1. Store `historyId` from Gmail's profile after every sync page batch.
2. `history.list?startHistoryId=<cursor>` returns change records: `messagesAdded`, `messagesDeleted`, `labelsAdded`, `labelsRemoved`.
3. Process per record type:
   - **Added, uncached** → full fetch + upsert, but only when the event carries `INBOX` and not SPAM/TRASH — spam arrivals are deliberately skipped.
   - **Added, cached** → METADATA label refresh.
   - **Labels changed, cached** → METADATA refresh → `update_email_labels` recomputes state/category/eligibility (no body transfer).
   - **Deleted** → `mark_email_excluded` (row preserved).
4. Re-read profile → new historyId → persist.

## Expiry recovery

Gmail expires history after ~30 days (or invalidates it on some operations) — the API answers 404/410. Alfred then falls back to a full INBOX listing that *also* refreshes labels for already-cached rows, then stores the fresh historyId. See [[Gmail Incremental Sync Flow]].

## Related

- [[Gmail Incremental Sync Flow]]
- [[Pagination]]
- [[Gmail Errors]]
