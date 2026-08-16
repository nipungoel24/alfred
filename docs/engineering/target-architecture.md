# Target Architecture

This document describes the hardened target architecture for Alfred's smart inbox processing flow.

## 1. Runtime Data Flow

```mermaid
flowchart TD
    Gmail[Gmail API] --> SyncService[Sync Service]
    SyncService --> |Batch Upsert| SQLite[SQLite (emails)]
    SyncService --> |Enqueue| SQLiteJobs[SQLite (jobs)]
    
    SQLiteJobs --> |Poll & Claim| AnalysisWorker[Analysis Worker]
    AnalysisWorker --> |Analyze| Ollama[Ollama Local LLM]
    Ollama --> |EmailAnalysis| AnalysisWorker
    
    AnalysisWorker --> |Email + Analysis| TaskDerivation[TaskDerivationService]
    TaskDerivation --> |Filtered Tasks| SQLiteTasks[SQLite (tasks/deadlines)]
    
    AnalysisWorker --> |Progress Event| SSE[Server-Sent Events]
    SSE --> |Debounced Update| ReactQuery[Frontend React Query Cache]
```

## 2. Module Ownership

- **SyncService:** Responsible exclusively for fetching raw email data from Gmail, mapping it to local schema, and doing batch-inserts. Does not perform analysis.
- **Repository (SQLite):** Acts as the central nervous system. Uses WAL mode for concurrent reads/writes. Owns job queue state.
- **AnalysisWorker:** A background asyncio task that polls `jobs`, handles retry mechanics, talks to `OllamaClient`, and broadcasts SSE.
- **TaskDerivationService:** Takes raw AI `EmailAnalysis` outputs and applies strict heuristic filtering (noise patterns, explicit vs implicit, third-party) to ensure user golden tasks are pristine.
- **Frontend (React Query + TanStack Virtual):** Manages local caching and virtualized lists (60FPS scrolling). Listens to SSE but debounces invalidations to prevent backend network request storms.

## 3. Worker Concurrency and Scale
- **Workers:** 1 background worker. Benchmarks proved multiple workers hitting Ollama simultaneously degrade total throughput and VRAM latency on typical consumer hardware.
- **Ollama Residency:** Ollama `keep_alive` is used to prevent model unloading between analyses.
- **SSE Events:** Frontend coalesces `analysis_complete` events via a 1s debounce to invalidate caches gracefully without freezing the UI.
