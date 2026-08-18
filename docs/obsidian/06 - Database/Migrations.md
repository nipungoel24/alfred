---
type: architecture
layer: database
status: active
tags:
  - database
---

# Migrations

Schema evolution is **additive and in-place** inside [[backend.app.db.database._migrate]], run on every `connect()` before indexes are created. There is no migration table and no down-migrations — every step is written to be idempotent.

## Migrations that exist

1. `emails`: added `account_id`, `thread_id`, `sender_col`, `subject_col`, `received_at_col`, then `label_ids_json`, `mailbox_state`, `gmail_category`, `pipeline_eligibility`.
2. **Label backfill**: rows with empty label columns but Gmail raw metadata in their payload get state/category/eligibility derived *in SQL* — no Gmail calls needed.
3. **Payload repair pass**: rows whose columns were backfilled by an older run but whose payload JSON still has empty `label_ids` get the payload patched so runtime reads agree with columns.
4. `tasks`: added `derivation_version`, `confidence`, `fingerprint`.
5. `jobs`: added `not_before` (scheduling/backoff).

## Rules

- Never destructive: no column drops, no table rebuilds that could lose source rows ([[Data Ownership]]).
- Backfills tolerate malformed payloads (skip row, keep going).
- New columns default to NULL → policy treats unknown state safely (legacy rows normalize to a typed backfill state at read time, [[backend.app.mail.backfill.normalize_cursor]]).

## Related

- [[Database Overview]]
- [[Data Ownership]]
- [[Application Startup Flow]]
