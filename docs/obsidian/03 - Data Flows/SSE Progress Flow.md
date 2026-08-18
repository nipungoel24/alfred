---
type: data-flow
layer: frontend
status: active
tags:
  - system
  - frontend
---

# SSE Progress Flow

How the UI learns that analysis finished — without polling endpoints.

```mermaid
sequenceDiagram
    participant W as Workers (analysis/backfill)
    participant BE as FastAPI (progress_subscribers)
    participant E as EventSource
    participant AP as AnalysisProgress
    participant Q as React Query

    W->>BE: _broadcast_progress(event)
    BE->>E: SSE event
    E->>AP: onmessage (parse)
    AP->>AP: setPending + latestEvent
    AP->>Q: debounced invalidation (1s): emails/counts/tasks/briefing
    Q->>BE: refetch active queries
    Note over E,BE: heartbeat every 15s keeps the connection alive
```

## Event vocabulary

`status`, `analysis_complete` (cached flag + ms), `analysis_error`, `analysis_cancelled`, `worker_paused`, `jobs_enqueued`, `backfill_progress`, `heartbeat`.

## Endpoint & consumer

- [[GET --api-analysis-progress]] — StreamingResponse over in-process queues (`progress_subscribers`); heartbeat keeps proxies from closing.
- [[frontend.src.components.ui.AnalysisProgress.AnalysisProgress|AnalysisProgress]] — renders the floating glass pill ("Analyzing N messages in background…") only while pending > 0; closes the EventSource on unmount.

## Failure posture

SSE drops are safe: the pill disappears, and any completed work is discovered on the next query refresh (React Query's normal cadence). This is why SSE is a *hint*, not the data source — see [[ADR-011 - SSE Progress]].

## Related

- [[Background Analysis Job Flow]]
- [[All Mail Backfill Flow]]
- [[Frontend Data Fetch Flow]]
