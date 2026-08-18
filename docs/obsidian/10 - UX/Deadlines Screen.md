---
type: architecture
layer: frontend
status: active
tags:
  - frontend
---

# Deadlines Screen

[[frontend.src.features.deadlines.DeadlinesPage.DeadlinesPage|DeadlinesPage]] — the time-bound commitments.

- Reads the briefing's `deadlines` list ([[GET --api-briefing]]) — the same eligibility-filtered source as Overview's Upcoming column.
- Rows: glowing accent dot, subject, sender + why-it-matters, due wording on the right.

## Limitation by design

Dates are the model's extracted strings, not normalized datetimes — no calendar math in Round 1 ([[Deadline Extraction Flow]]).

## Related

- [[Tasks Screen]]
- [[Briefing Generation Flow]]
