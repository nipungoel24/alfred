---
type: architecture
layer: database
status: active
tags:
  - database
---

# Data Ownership

Who owns each byte, and the rules that keep owners from stepping on each other.

## The three classes

| Class | Tables | Rules |
|---|---|---|
| **Source data** | [[emails]] | Written by Gmail sync only. Never deleted to hide mail — spam/trash/archive transitions flip `mailbox_state`/`pipeline_eligibility`. Deleted only when Gmail reports permanent deletion (still row-preserving via `mark_email_excluded`) or the user removes the account. |
| **Derived data** | [[email_analysis]], [[inbox_briefing]], [[inference_metrics]] | Regenerable at any time from source + model. Cache keys (content fingerprint / briefing fingerprint) make staleness impossible rather than likely. |
| **User state** | [[accounts]], [[credentials]], task `status`/existence | Never overwritten by derivation. Migrations reconcile *toward* user state ([[backend.app.services.task_migration.TaskMigrationService|TaskMigrationService]]). |
| **Process state** | [[jobs]] | Durable queue; the workers' memory. |

## Projection, not deletion

The central doctrine: **"source email data ≠ active Alfred attention data."** A message that leaves the inbox keeps its row, its analysis, and its derived tasks historically — but every *current* projection (briefing, overview attention, needs-reply, active tasks, deadlines, queue) joins against eligibility. See [[backend.app.mail.eligibility.MailEligibilityPolicy|MailEligibilityPolicy]] and [[backend.app.db.repositories.Repository.active_tasks]].

## Enforcement points

- `mark_email_excluded` (not `DELETE`) for Gmail deletions.
- `_briefing_eligible_emails` filters at query time, not creation time.
- Task rebuild skips ineligible sources but preserves user statuses.
- Worker re-checks eligibility at pickup — a mid-queue spam move cancels the job.

## Related

- [[Derived Data]]
- [[Threat Model]]
- [[ADR-009 - Versioned Task Derivation]]
