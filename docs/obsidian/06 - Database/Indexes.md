---
type: architecture
layer: database
status: active
tags:
  - database
---

# Indexes

Declared in `INDEXES` in [[backend.app.db.database]] (generated note: [[table_indexes]]). Deliberately kept to the access patterns that exist.

| Index | Serves |
|---|---|
| `idx_emails_account_imported` | per-account chronological listings |
| `idx_emails_thread` | thread lookups (draft context) |
| `idx_emails_received` | global recency ordering |
| `idx_emails_state_category` | inbox scope + category tabs (account, state, category, received) |
| `idx_emails_state_received` | All Mail scope + counts (covering) |
| `idx_emails_eligibility` | pipeline-eligibility filtering |
| `idx_analysis_email` | analysis lookups |
| `idx_tasks_status` / `idx_tasks_source` / `idx_tasks_thread` | task projections |
| `idx_jobs_status_priority` / `idx_jobs_status_notbefore` | worker dequeue + backoff |

Verified with `EXPLAIN QUERY PLAN` during development: category filtering and scope counts hit their compound indexes; inbox listings trade the state/category index against the recency index depending on the planner.

## Related

- [[Database Overview]]
- [[Migrations]]
