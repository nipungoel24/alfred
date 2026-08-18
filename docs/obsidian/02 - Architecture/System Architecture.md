---
type: architecture
layer: meta
status: active
tags:
  - system
  - architecture
---

# System Architecture

Alfred is a three-process desktop system: a React frontend, a FastAPI backend (compiled to a native sidecar), and a local Ollama runtime — plus Gmail as the only external service.

```mermaid
flowchart LR
    subgraph desktop[Tauri Desktop Shell]
        UI[React Frontend :5173]
        BE[FastAPI Sidecar :8765]
    end
    subgraph local[On-device services]
        OL[Ollama :11434 qwen3:4b]
        DB[(SQLite AppData)]
    end
    G[Gmail API]

    UI -- "REST + SSE" --> BE
    UI -- "devUrl (dev) / bundled dist" --> desktop
    BE --> DB
    BE -- "gmail.readonly OAuth2" --> G
    BE -- "loopback /api/generate" --> OL
    BE -- "spawns at setup" --> desktop
```

## Process boundaries

| Process | Role | Port | Lifecycle |
|---|---|---|---|
| React + Vite frontend | All UI; React Query data layer; SSE consumer | 5173 (dev) | bundled into Tauri in production |
| FastAPI backend | OAuth, Gmail sync, AI orchestration, SQLite, SSE | 8765 | compiled sidecar, spawned by Tauri ([[Sidecar Architecture]]) |
| Ollama | Local LLM serving | 11434 | user-installed, external to Alfred |

## The core loop

Gmail state → local mirror ([[emails]]) → eligibility/category layer ([[backend.app.mail.eligibility.MailEligibilityPolicy|MailEligibilityPolicy]]) → durable analysis queue ([[jobs]]) → local AI ([[backend.app.ai.service.AIService|AIService]]) → derived projections ([[email_analysis]], [[tasks]], [[inbox_briefing]]) → UI ([[frontend.src.mail.MailWorkspace.MailWorkspace|MailWorkspace]], [[frontend.src.features.overview.OverviewPage.OverviewPage|OverviewPage]], [[frontend.src.intelligence.IntelligencePanel.IntelligencePanel|IntelligencePanel]]).

```mermaid
flowchart TD
    G[Gmail] -->|"OAuth + historyId sync"| S[Sync Layer]
    S --> E[(emails)]
    E --> P[MailEligibilityPolicy]
    P --> Q[(jobs)]
    Q --> W[Analysis Worker]
    W --> AI[Ollama qwen3:4b]
    AI --> A[(email_analysis)]
    A --> T[Task Derivation]
    T --> TK[(tasks)]
    A --> B[Briefing]
    B --> BR[(inbox_briefing)]
    A --> UI[Frontend]
    TK --> UI
```

## Key invariants

1. Gmail is the source of truth for mailbox state; Alfred never invents it.
2. Source rows are never deleted to hide mail — eligibility is a projection ([[Data Ownership]]).
3. Derived projections never outrank user state ([[ADR-008 - Separate Action Candidates From Tasks]]).
4. Every durable loop (analysis, backfill) survives restart via SQLite state ([[jobs]], [[accounts]]).

## Explore deeper

- [[Backend Architecture]]
- [[Frontend Architecture]]
- [[Gmail Architecture]]
- [[AI Architecture]]
- [[Database Architecture]]
- [[Security Architecture]]
- [[Desktop Architecture]]
- [[Runtime Lifecycle]]
