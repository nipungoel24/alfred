---
type: architecture
layer: test
status: active
tags:
  - test
---

# Migration Testing

Tests that prove data survives rule changes — [[backend.tests.test_task_migration]] (+ the migration integration test referenced in git history).

## What must hold (and is tested)

1. **Idempotency** — running the migration twice changes nothing.
2. **User-state preservation** — completed/dismissed tasks keep id/status/created_at through re-derivation.
3. **Fingerprint reconciliation** — same logical task (thread+action) maps to the same row; new actions create new rows; obsolete pending tasks are pruned.
4. **Source untouched** — migration never writes [[emails]] or [[email_analysis]].
5. **Ineligible sources** — analyses of spam/archived mail don't resurrect tasks during rebuild.

## Related

- [[Task Derivation Flow]]
- [[ADR-009 - Versioned Task Derivation]]
- [[Migrations]]
