---
type: architecture
layer: frontend
status: active
tags:
  - frontend
---

# Overview Screen

[[frontend.src.features.overview.OverviewPage.OverviewPage|OverviewPage]] — the morning command center, deliberately not an admin dashboard.

## Layout (editorial)

1. Gradient greeting + "N messages in Inbox · M in All Mail" subline.
2. Flat glass metric tiles: Important / Needs Reply / Deadlines / Inbox (accent top-edge on hover, click-through to views).
3. Two columns:
   - **Needs attention** — hairline rows in a glass panel (badges: priority, Reply).
   - **Upcoming** — deadline rows with accent due text.
4. **Alfred briefing** — violet accent-washed panel, refresh action; executive summary text.

## Data

[[GET --api-briefing]], emails (attention fallback when briefing lacks items), [[GET --api-emails-counts]]. Refresh uses [[POST --api-briefing-generate]] with targeted invalidation.

## Related

- [[Briefing Generation Flow]]
- [[Design System]]
- [[User Journeys]]
