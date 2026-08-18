---
type: database-table
layer: database
status: active
source: backend/app/db/database.py
tags:
  - database
---

# inbox_briefing

Cache for the executive briefing. One row per briefing fingerprint.

## Data classification

**Derived cache.** `fingerprint` (PK) hashes the *analyses* of the eligible email set + schema version + model — any change in the eligible set invalidates it ([[backend.app.mail.briefing_fingerprint.briefing_fingerprint]]).

## Written By

- [[POST --api-briefing-generate]] via [[backend.app.db.repositories.Repository.save_briefing]]

## Read By

- [[GET --api-briefing]]

Schema detail: [[table_inbox_briefing]].

## Related

- [[Briefing Generation Flow]]
- [[email_analysis]]
