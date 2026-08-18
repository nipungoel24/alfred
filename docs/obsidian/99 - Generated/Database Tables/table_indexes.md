---
type: database-table
generated: true
layer: database
source: backend/app/db/database.py
status: active
tags: [database, database-table]
---

# table_indexes

> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.

## Indexes (as declared in `INDEXES`)

```sql
CREATE INDEX IF NOT EXISTS idx_emails_account_imported ON emails(account_id, imported_at DESC);
CREATE INDEX IF NOT EXISTS idx_emails_thread ON emails(thread_id);
CREATE INDEX IF NOT EXISTS idx_emails_received ON emails(received_at_col DESC);
CREATE INDEX IF NOT EXISTS idx_emails_state_category ON emails(account_id, mailbox_state, gmail_category, received_at_col DESC);
CREATE INDEX IF NOT EXISTS idx_emails_state_received ON emails(mailbox_state, received_at_col DESC);
CREATE INDEX IF NOT EXISTS idx_emails_eligibility ON emails(pipeline_eligibility);
CREATE INDEX IF NOT EXISTS idx_analysis_email ON email_analysis(email_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_source ON tasks(source_email_id);
CREATE INDEX IF NOT EXISTS idx_tasks_thread ON tasks(source_thread_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status_priority ON jobs(status, priority DESC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_jobs_status_notbefore ON jobs(status, not_before);
```

## Related

- [[Indexes]]