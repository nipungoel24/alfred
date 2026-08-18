---
type: architecture
layer: meta
status: active
tags:
  - architecture
---

# Dependency Map

Who depends on whom, at the subsystem level — the machine-readable version lives in `99 - Generated/dependency-graph.json`.

```mermaid
flowchart TD
    FE[Frontend] -->|REST+SSE| API[FastAPI routes]
    API --> R[Repository]
    API --> G[GmailProvider]
    API --> AS[AIService]
    R --> DB[(SQLite)]
    G --> DB
    G --> E[MailEligibilityPolicy]
    AS --> O[OllamaClient]
    W1[Analysis worker] --> AS
    W2[Backfill worker] --> G
    W1 --> TD[Task derivation]
    TD --> DB
    API --> TD
    TD --> TM[TaskMigrationService]
    G --> BF[mail.backfill cursor]
    W2 --> BF
```

## Dependency rules worth knowing

- `schemas` is depended on by everything, depends on nothing.
- `eligibility` is depended on by provider + repository + main; it depends on nothing but its own constants.
- Only `gmail.py` knows Gmail's wire format; only `repositories.py` knows SQL.
- The frontend depends only on the HTTP/SSE surface — never on tables or internals.

## Related

- [[Backend Code Map]]
- [[Frontend Code Map]]
- [[Critical Execution Paths]]
