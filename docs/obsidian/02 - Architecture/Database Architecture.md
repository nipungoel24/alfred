---
type: architecture
layer: database
status: active
tags:
  - system
  - architecture
  - database
---

# Database Architecture

One SQLite file (`%LOCALAPPDATA%/Alfred/alfred.sqlite3`), WAL mode, created and migrated by [[backend.app.db.database.connect]]. All access flows through [[backend.app.db.repositories.Repository]]; routes and workers never issue raw SQL (the one exception is startup housekeeping in `lifespan`).

## Schema

```mermaid
erDiagram
    accounts ||--o| credentials : "1:1 DPAPI tokens"
    accounts ||--o{ emails : "owns sync cursor"
    emails ||--o| email_analysis : "content_hash keyed"
    emails ||--o{ tasks : "source_email_id"
    emails_fts ||--o| emails : "rowid FTS index"
    inbox_briefing }o--|| emails : "fingerprint of eligible set"
    jobs }o--o{ emails : "target_id"
    jobs ||--o{ inference_metrics : "job_id"

    accounts { text id PK; text provider; text sync_cursor }
    credentials { text account_id PK,FK; blob encrypted_refresh_token }
    emails { text id PK; text payload; text mailbox_state; text gmail_category }
    email_analysis { text email_id PK,FK; text payload; text content_hash }
    tasks { text id PK; text source_email_id FK; text fingerprint }
    jobs { text id PK; text job_type; integer priority; text not_before }
    inbox_briefing { text fingerprint PK; text payload }
    inference_metrics { integer id PK; text job_id; integer total_ms }
    emails_fts { subject; sender; body }
```

## Classifying the data

| Table | Classification | Details |
|---|---|---|
| [[accounts]] | User state | connection info + sync cursors |
| [[credentials]] | Secrets | DPAPI ciphertext only |
| [[emails]] | **Source data** | the local mirror — never deleted to hide mail |
| [[email_analysis]] | Derived (cached) | keyed by content fingerprint |
| [[tasks]] | Derived + user state | reconciled, not destroyed |
| [[jobs]] | Durable queue | the process-memory |
| [[inbox_briefing]] | Derived cache | fingerprint-keyed |
| [[inference_metrics]] | Telemetry | per-inference timings |

See [[Data Ownership]] and [[Derived Data]] for the rules that keep source data and projections separate.

## Concurrency & durability

- Single process, two workers + request handlers → one SQLite connection, `check_same_thread=False`, WAL + `busy_timeout=5000`.
- Durable loops use the [[jobs]] table with `not_before` scheduling so a crash never loses work ([[Background Analysis Job Flow]], [[All Mail Backfill Flow]]).
- Migrations are additive `ALTER TABLE` steps with safe in-place backfills — see [[Migrations]].

## Related

- [[Database Overview]]
- [[Indexes]]
- [[Transactions]]
