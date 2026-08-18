---
type: database-table
layer: database
status: active
source: backend/app/db/database.py
tags:
  - database
---

# email_analysis

Cached AI verdicts per email — the "intelligence projection" of [[emails]].

## Data classification

**Derived (cache).** Keyed by `email_id` (PK, FK cascade) but *validated* by `content_hash` + `model_name` + `schema_version`: if the email content changed, the cached analysis no longer matches and is recomputed.

## Payload

JSON of [[backend.app.schemas.EmailAnalysis]]: short_summary, category, priority, priority_score, reason_for_priority, needs_reply, action_items, deadlines.

## Written By

- [[backend.app.main._analysis_worker]] (via [[backend.app.db.repositories.Repository.save_analysis]])
- [[POST --api-emails-{email_id}-analyze]]

## Read By

- [[GET --api-emails]] (attach analyses to rows)
- [[backend.app.main._briefing_eligible_emails]]
- [[backend.app.services.task_derivation.rebuild_tasks_from_analyses|rebuild_tasks_from_analyses]]
- [[frontend.src.intelligence.IntelligencePanel.IntelligencePanel|IntelligencePanel]] via the emails API

## Cache invalidation

Content fingerprint mismatch → miss; eligibility changes do NOT delete analyses (they are hidden by projections, not destroyed — [[Data Ownership]]).

Schema detail: [[table_email_analysis]].

## Related

- [[emails]]
- [[tasks]]
- [[AI Caching]]
