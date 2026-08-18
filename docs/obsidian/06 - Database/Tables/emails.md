---
type: database-table
layer: database
status: active
source: backend/app/db/database.py
tags:
  - database
---

# emails

The local mail mirror — the **source of truth for Alfred's copy** of Gmail.

## Data classification

**Source data.** Never deleted merely to hide mail: spam/trash/archived transitions update `mailbox_state`/`pipeline_eligibility` and the row stays ([[Data Ownership]]).

## Key columns

- `id` — Gmail message id (PK); `payload` — full `Email` JSON (incl. body + lean gmail_raw metadata); `content_hash` — [[backend.app.mail.fingerprint.content_fingerprint]].
- `account_id`, `thread_id`, `sender_col`, `subject_col`, `received_at_col` — query columns.
- `label_ids_json` — Gmail label IDs (source of truth for state).
- `mailbox_state` / `gmail_category` / `pipeline_eligibility` — derived per [[backend.app.mail.eligibility.MailEligibilityPolicy]] at write time; recomputed on label history events.

Schema detail: [[table_emails]]. FTS mirror: [[table_emails_fts]].

## Written By

- [[backend.app.mail.providers.gmail.GmailProvider.sync_messages]] (import + label refresh)
- [[backend.app.mail.providers.gmail.GmailProvider.backfill_messages]]
- [[backend.app.db.repositories.Repository.upsert_email]] / `update_email_labels` / `mark_email_excluded`
- [[POST --api-emails-import]] (legacy CSV ingest)

## Read By

- Every inbox/All Mail/search endpoint ([[GET --api-emails]], [[GET --api-emails-{email_id}]])
- [[backend.app.main._analysis_worker]] (analyze targets)
- Briefing eligibility + task projections (joins)

## Related

- [[email_analysis]]
- [[tasks]]
- [[Gmail Incremental Sync Flow]]
