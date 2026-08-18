---
type: data-flow
layer: gmail
status: active
tags:
  - system
  - gmail
  - critical-path
---

# All Mail Backfill Flow

How the full non-spam/non-trash mailbox arrives locally without hammering Gmail or blocking the product.

```mermaid
sequenceDiagram
    participant C as Account cursor (backfill_state)
    participant W as Backfill Worker
    participant P as GmailProvider.backfill_messages
    participant G as Gmail
    participant R as Repository

    W->>R: next_job('backfill_gmail', not_before ok)
    W->>P: one bounded page (q=-label:INBOX, 40, includeSpamTrash=false)
    P->>G: messages.list?pageToken
    G-->>P: {messages, resultSizeEstimate, nextPageToken}
    loop each message
        alt cached
            P->>R: update_email_labels (skip body)
        else new
            P->>G: GET messages/{id}
            P->>R: upsert_email (labels/state/category/eligibility)
        end
    end
    P->>R: record_success: counters + page token + estimate → cursor
    alt has_more
        R->>R: requeue_job(not_before = +2.5s)
    else complete
        R->>R: backfill_state = complete, job succeeded
    end
```

## Typed state machine

`backfill_state` in the [[accounts]] sync cursor: `not_started → running → complete` (with `paused` for user pause and `failed` after the retry budget). See [[backend.app.mail.eligibility.BackfillState]] and [[backend.app.mail.backfill]].

## Ownership & resilience

- **Backend owns the loop.** The frontend only observes (`/api/accounts` carries the status payload); closing the UI never pauses sync.
- **One durable job row per account** (`backfill_gmail_<id>`, priority 5 — always below analysis jobs). Each page re-queues the *same* row with `not_before` rate limiting; no job explosion.
- **Failure budget**: transient Gmail errors → `retryable_failed` + exponential backoff (30s → 5m cap) via `not_before`; 401/403 or exhausted attempts → `failed` state.
- **Restart resumes** exactly: startup re-arms the job when state is `not_started`/`running` ([[Application Startup Flow]]). Verified against the real mailbox with zero duplicates.

## Data notes

- The query is `-label:INBOX` — archived + sent arrive; spam/trash never (flag enforced), drafts aren't in `messages.list`.
- `resultSizeEstimate` is captured but treated as approximate (Gmail's number is volatile; UI shows "~N remaining").
- Imported archived/sent rows are **not** enqueued for analysis ([[backend.app.mail.eligibility.MailEligibilityPolicy|MailEligibilityPolicy]]).

## Endpoints

- [[POST --api-accounts-{account_id}-backfill]] — start/resume
- [[POST --api-accounts-{account_id}-backfill-pause]] — pause
- [[GET --api-accounts-{account_id}-backfill]] — observe status

## Tests

- [[backend.tests.test_backfill_jobs.test_backfill_job_is_single_durable_row]]
- [[backend.tests.test_allmail.test_backfill_first_page_and_resume]]
- [[backend.tests.test_backfill_jobs.test_backoff_and_promotion_cycle]]

## Related

- [[Gmail Incremental Sync Flow]]
- [[Pagination]]
- [[backend.app.main._backfill_worker]]
