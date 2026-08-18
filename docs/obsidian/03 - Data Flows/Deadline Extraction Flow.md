---
type: data-flow
layer: ai
status: active
tags:
  - system
  - ai
---

# Deadline Extraction Flow

How time-bound commitments travel from raw email to the UI.

1. **Extraction** — [[backend.app.ai.service.AIService.analyze_email]] prompts for `deadlines[]` (description + `due_at` + confidence). The prompt forbids inventing dates; relative wording ("Friday", "5 PM today") is preserved verbatim when no calendar date is present, and ambiguous timing ("soon") must be omitted. See [[Prompt Architecture]] and [[backend.app.schemas.Deadline]].
2. **Schema validation** — Pydantic enforces the shape; `confidence` is `explicit` | `inferred`.
3. **Persistence** — deadlines live inside [[email_analysis]] payloads (no separate table).
4. **Task projection** — [[backend.app.services.task_derivation.derive_tasks]] creates deadline-tasks **only** for `explicit` confidence entries; inferred ones stay informational.
5. **Briefing projection** — [[backend.app.ai.service.AIService.generate_inbox_briefing]] surfaces deadlines from eligible analyses; `deadline_count` is recomputed locally (never trusted from the model).
6. **UI** — [[frontend.src.features.deadlines.DeadlinesPage.DeadlinesPage|DeadlinesPage]] reads the briefing; the [[frontend.src.intelligence.IntelligencePanel.IntelligencePanel|IntelligencePanel]] shows per-message deadlines; task rows show `due_at`.

## Known limitations (by design)

- Dates are raw strings, not normalized datetimes — no calendar math in Round 1 ([[Round 1 Scope]]).
- "Inferred" deadlines are visible in analysis but do not become tasks — conservative by design.

## Tests

- Golden corpus covers explicit vs inferred deadlines: [[Golden Email Corpus]].
- Derivation gating: [[backend.tests.test_task_derivation]].

## Related

- [[Task Derivation Flow]]
- [[Briefing Generation Flow]]
- [[frontend.src.features.deadlines.DeadlinesPage.DeadlinesPage|DeadlinesPage]]
