---
type: architecture
layer: frontend
status: active
tags:
  - frontend
---

# Intelligence Pane Screen

[[frontend.src.intelligence.IntelligencePanel.IntelligencePanel|IntelligencePanel]] — Alfred's AI differentiator, rendered as a calm floating companion.

## Surface

Elevated solid surface (reader-surface tokens), margin + 14px radius + soft shadow; 336px; independent scroll; pane-in reveal; overlays at <1440px.

## Hierarchy

Header `ALFRED INTELLIGENCE` (uppercase, sparkles icon) → sections with uppercase muted labels and bigger content type:

- **Summary** — the model's short summary.
- **Why it matters** — reason_for_priority.
- **Priority** — level badge, score /100, Needs Reply yes/no (key-value rows).
- **Deadline** — deadline items with due wording.
- **Tasks** — action items with due dates.
- **Reply** — *Generate Draft* (gradient violet primary) → `draft-panel` editor-like output with violet left rule; scoped error banner on Ollama failure.

Empty sections are hidden entirely; unanalyzed mail shows the "analysis pending" state with an explanation.

## Data

Reads the message's analysis (attached by the emails API); mutates via the draft endpoint ([[Draft Generation Flow]]).

## Related

- [[Email Reader Screen]]
- [[Analysis Schema]]
- [[AI Failure Handling]]
