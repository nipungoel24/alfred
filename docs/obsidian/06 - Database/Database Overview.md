---
type: architecture
layer: database
status: active
tags:
  - database
  - architecture
---

# Database Overview

Single SQLite file at `%LOCALAPPDATA%/Alfred/alfred.sqlite3` (configurable via `ALFRED_DATABASE_PATH`). Created/migrated by [[backend.app.db.database.connect]]; accessed exclusively through [[backend.app.db.repositories.Repository]].

## Tables at a glance

| Table | Purpose | Classification |
|---|---|---|
| [[accounts]] | Connected mail providers + sync/backfill cursors | User state |
| [[credentials]] | DPAPI-encrypted OAuth tokens | Secrets |
| [[emails]] | The local mail mirror (source data) | Source |
| [[email_analysis]] | Cached AI verdicts keyed by content fingerprint | Derived |
| [[tasks]] | User-actionable projections (reconciled) | Derived + user state |
| [[jobs]] | Durable analysis/backfill queue | Process state |
| [[inbox_briefing]] | Cached executive briefing | Derived |
| [[inference_metrics]] | Per-inference timing/telemetry | Telemetry |
| [[table_emails_fts]] | FTS5 full-text index of emails | Index |

## Engine settings

WAL journal, `synchronous=NORMAL`, `busy_timeout=5000`, 8MB page cache, FTS5 (`unicode61`). See [[Transactions]].

## Schema evolution

Additive migrations with in-place backfills (labels/eligibility columns, payload repair) — [[Migrations]].

## Related

- [[Database Architecture]]
- [[Data Ownership]]
- [[Derived Data]]
- [[Indexes]]
