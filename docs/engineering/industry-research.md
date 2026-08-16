# Alfred Engineering Research — Industry & Official Documentation Review

*Prepared: August 2026*

This document captures research findings from current official documentation and industry best practices, evaluated specifically for Alfred's architecture: a single-user, local-first, Windows desktop Gmail smart inbox.

---

## 1. Ollama Inference Engine

### Current Official Guidance

| Area | Official Behavior |
|---|---|
| **Structured output** | Pass `format` parameter as JSON Schema object to `/api/generate` or `/api/chat`. Provides grammar-constrained decoding. |
| **`keep_alive`** | Controls how long model stays in VRAM after request. `-1` = indefinitely, `"5m"` = 5 minutes, `0` = immediate unload. |
| **Model preload** | Send empty request with `keep_alive: -1` to force model load before first real request. |
| **`OLLAMA_NUM_PARALLEL`** | Server env var controlling concurrent requests per model. Each parallel slot allocates context memory. Default: 1. |
| **Response metrics** | `/api/generate` returns `total_duration`, `load_duration`, `prompt_eval_duration`, `prompt_eval_count`, `eval_duration`, `eval_count` in nanoseconds. |
| **`think` parameter** | `think: false` suppresses reasoning chain output, keeping only the structured response. |

### What Alfred Currently Does

- Uses `/api/generate` with `stream: false`, `think: false`, schema via `format` parameter. ✓
- Uses 90-second timeout globally. Insufficient for cold model loads.
- Does NOT preload the model at startup.
- Does NOT use `keep_alive`.
- Does NOT capture or record response metrics.
- Does NOT implement concurrency control — requests are sequential from frontend loop.
- Strips `<think>` tags from response as fallback. Fragile but functional.

### Gap Analysis

| Gap | Impact |
|---|---|
| No model preload | First inference after backend start may take 10-30s for model load. |
| No `keep_alive` | Model may unload between requests during batch analysis, causing repeated cold loads. |
| No metrics capture | Cannot measure or optimize inference performance. |
| No concurrency control | Sequential analysis is safe but slow for large batches. |
| No retry/error classification | One Ollama failure shows global "inference failed" banner. |
| Fixed 90s timeout | May be too short for cold load + inference; too long for a hung request. |

### Recommended Alfred Approach

1. **Preload on startup**: Send `{"model": "qwen3:4b", "keep_alive": -1}` during FastAPI lifespan startup.
2. **Set `keep_alive: "30m"`** on every inference request to prevent unload during batch processing.
3. **Capture all response metrics** (total_duration, load_duration, prompt_eval_count, eval_count, eval_duration) and persist to local metrics table.
4. **Default concurrency: 1**. Benchmark 2 only if hardware demonstrates benefit without VRAM thrashing.
5. **Classify errors**: `OLLAMA_UNAVAILABLE`, `OLLAMA_TIMEOUT`, `OLLAMA_INVALID_JSON`, `OLLAMA_MODEL_MISSING`.
6. **Retry strategy**: 1 retry with 2s backoff for transient failures. Mark failed after 2 attempts.
7. **Adaptive timeout**: 120s for first request (cold load possible), 90s thereafter.

### Rejected Alternatives

- **High parallelism (4+)**: Each parallel slot allocates context memory. On consumer GPUs (8-12GB VRAM), this causes thrashing. Rejected.
- **Streaming responses**: Adds complexity for structured JSON extraction with no user-facing benefit (user sees analysis result, not token stream). Rejected.
- **External inference queue (Celery/Redis)**: Massively over-engineered for a single-user desktop app. Rejected.

---

## 2. Gmail API

### Current Official Guidance (2026 Quota Model)

| Operation | Quota Units | Notes |
|---|---|---|
| `messages.list` | 5 units | Returns only message IDs |
| `messages.get` | 20 units | Full message payload |
| `history.list` | 5 units | Incremental changes since historyId |
| Batch request | Sum of individual calls | Up to 100 sub-requests per batch |
| Per-user limit | 6,000 units/min | Per user per project |

### What Alfred Currently Does

- Lists INBOX messages with `maxResults: 50`. ✓
- Fetches each message individually with full payload. ✗ (no batching, no `fields` parameter)
- Uses `history.list` for incremental sync. ✓
- Falls back to full sync on 404/410. ✓
- Stores `historyId` and `nextPageToken` in `sync_cursor`. ✓
- No `format=metadata` optimization for initial scan.
- No batch requests.
- Stores entire `gmail_raw` response in `source_metadata`. Wastes storage.

### Gap Analysis

| Gap | Impact |
|---|---|
| Individual message fetches | 50 messages = 50 HTTP requests = 1000 quota units. Batch would be 1 HTTP request. |
| No `fields` parameter | Fetches entire message payload including attachments metadata when only headers + body needed. |
| Full `gmail_raw` in source_metadata | Massive storage bloat. A single email's raw Gmail response can be 50-100KB+ with HTML. |
| No exponential backoff on rate limits | Could hit 429 errors under heavy sync. |

### Recommended Alfred Approach

1. **Use `fields` parameter** on `messages.get`: `id,threadId,internalDate,payload(headers,parts(mimeType,body(data)),body(data),mimeType)`. Reduces response size by ~60%.
2. **Batch API requests**: Bundle up to 50 `messages.get` calls per batch HTTP request. Reduces round-trips from 50 to 1.
3. **Remove `source_metadata.gmail_raw`**: Store only extracted/normalized fields. Saves ~80% storage per email.
4. **Implement exponential backoff** for 429/5xx errors.
5. **Use `format=metadata`** for a quick initial scan pass where only subjects/senders are needed for priority sorting.

### Rejected Alternatives

- **`messages.batchGet`**: Does not exist in Gmail API. Must use generic HTTP batch mechanism. Not rejected, but noted.
- **Push notifications (Pub/Sub)**: Requires cloud infrastructure. Incompatible with local-first architecture. Rejected.
- **Full IMAP sync**: Out of scope for Round 1 (Gmail only). Rejected.

---

## 3. FastAPI Architecture

### Current Official Guidance

- **Lifespan context manager**: Replace deprecated `@app.on_event`. Use `@asynccontextmanager` for startup/shutdown.
- **Background workers**: Use `asyncio.Queue` + `asyncio.create_task` for in-process background work.
- **`BackgroundTasks`**: For fire-and-forget per-request work. Not suitable for persistent queue processing.
- **Resource cleanup**: Cancel and await background tasks during shutdown phase of lifespan.

### What Alfred Currently Does

- No lifespan manager. Resources created at module level.
- No background worker. Analysis runs synchronously in request handler.
- All business logic in `main.py` (304 lines, 15+ route handlers, OAuth state, PKCE generation, sync orchestration, analysis, briefing, task management).
- No graceful shutdown.
- No structured error hierarchy beyond `OllamaUnavailable`.

### Gap Analysis

| Gap | Impact |
|---|---|
| No lifespan | No model preload, no worker startup, no graceful shutdown. |
| Monolithic main.py | All concerns mixed: OAuth, sync, analysis, briefing, tasks. Hard to test and maintain. |
| Synchronous analysis in sync handler | `POST /sync` blocks until ALL emails are analyzed by Ollama. User waits minutes. |
| No background queue | Frontend drives analysis loop, blocking UI during batch processing. |
| Module-level resource creation | Database connection, AI service created at import time. No cleanup. |

### Recommended Alfred Approach

1. **Implement lifespan** with model preload, worker startup, graceful shutdown.
2. **Split routes** into separate router modules: accounts, emails, sync, analysis, tasks, briefing.
3. **Background analysis worker** using `asyncio.Queue` consumed by a persistent `asyncio.Task`.
4. **Sync endpoint** returns immediately after storing emails; enqueues analysis jobs.
5. **SSE endpoint** for analysis progress streaming to frontend.

---

## 4. SQLite Performance

### Current Official Guidance

| Setting | Recommended | Reason |
|---|---|---|
| `journal_mode` | `WAL` | Concurrent readers + single writer. No reader-writer blocking. |
| `synchronous` | `NORMAL` | Safe in WAL mode. Reduces fsync operations. |
| `busy_timeout` | `5000` (ms) | Prevents SQLITE_BUSY errors under contention. |
| `BEGIN IMMEDIATE` | For write transactions | Prevents upgrade deadlocks. |
| `PRAGMA optimize` | Periodically | Maintains query planner statistics. |

### What Alfred Currently Does

- Default journal mode (DELETE). No WAL.
- Default synchronous (FULL). Excessive for local desktop.
- No busy_timeout.
- `commit()` after EVERY individual operation (upsert_email, save_task, save_analysis, etc.). ~50 commits for 50 emails.
- No indexes beyond PRIMARY KEY.
- No FTS5.
- Stores entire `Email` Pydantic model as JSON blob in `payload` column. Queries must deserialize all rows to filter.

### Gap Analysis

| Gap | Impact |
|---|---|
| No WAL | Readers block writers during sync. |
| Individual commits | 50 emails = 50 fsync operations. Very slow on mechanical drives. |
| No indexes on account_id, thread_id, received_at | Full table scans for filtered queries. |
| JSON blob storage | Cannot query by sender, subject, date at SQL level. Must load all rows into Python to filter. |
| No FTS5 | Search loads ALL emails into Python and does string matching. O(N) for every keystroke. |

### Recommended Alfred Approach

1. **Enable WAL, NORMAL synchronous, busy_timeout=5000** on connection.
2. **Batch commits**: Wrap sync import in a single transaction.
3. **Add indexes**: `emails(account_id, imported_at)`, `emails(thread_id)`, `tasks(status, created_at)`, `tasks(source_email_id)`.
4. **Add searchable columns** to emails table: `sender`, `subject`, `received_at` as extracted columns alongside the JSON payload. Enables SQL-level filtering.
5. **Implement FTS5** for subject + body text search.
6. **Run `PRAGMA optimize`** on startup.

---

## 5. Frontend Architecture

### TanStack Query

- Replace manual `useState` + `useEffect` + `setInterval` polling with declarative query cache.
- Use `staleTime: 10_000` (10s) to prevent unnecessary refetches for a local backend.
- Use `invalidateQueries` after mutations (sync, analyze, toggle task) instead of manual `load()`.
- Prefetch email detail on hover for instant navigation.

### TanStack Virtual

- Virtualize email list and task list for 500+ items.
- Use stable row keys (email ID, task ID).
- Recent 2026 updates: cold mount <2ms for 10K items. Production-ready.

### Current Frontend Problems

- **App.tsx is 723 lines** containing all pages, all state, all handlers.
- **10-second polling interval** refetches ALL data (accounts, tasks, emails, briefing) every 10 seconds regardless of changes.
- **No virtualization**: All email rows rendered simultaneously.
- **Search runs in Python** via API call that loads all emails then filters in Python.
- **Analysis driven from frontend**: `for` loop in `handleSync` calls `analyze()` sequentially, blocking UI.

---

## 6. Progress Communication

### Recommended: Server-Sent Events (SSE)

- One-way server→client. Perfect fit for analysis progress.
- Built-in browser reconnection via `EventSource` API.
- Works over standard HTTP. No WebSocket upgrade needed.
- FastAPI supports SSE via `StreamingResponse` with async generators.

### Rejected: WebSocket

- Bidirectional not needed. Analysis progress is server→client only.
- More complex connection management.
- No benefit over SSE for this use case.

### Rejected: Short Polling

- Current approach (10s interval fetching everything). Wasteful and laggy.
- Replaced by SSE for real-time progress + TanStack Query with smart invalidation for data.

---

## 7. Task Derivation Quality

### Current Problem

50 emails → 91 tasks. Includes garbage like "Decode the base64 string" and "Verify TikTok credentials."

### Root Cause Analysis

1. **Every `action_item` from AI becomes a task unconditionally** (lines 55-69 in `repositories.py`).
2. **Every `deadline` from AI becomes a separate task** (lines 71-85), causing duplication when an action_item already has a deadline.
3. **No ownership validation**: Tasks created even when the action is assigned to someone else or is a newsletter CTA.
4. **No confidence threshold**: Low-confidence AI hallucinations become user tasks.
5. **Task creation is a side effect of `save_analysis()`**: Business logic buried in repository layer.

### Required Changes

1. **Separate TaskDerivationService** with explicit validation.
2. **Ownership rule**: Only create tasks when evidence shows USER is expected to act.
3. **Confidence scoring**: Suppress low-confidence candidates.
4. **Deduplication**: Stable fingerprint based on `(thread_id, normalized_action, deadline)`.
5. **No tasks from**: newsletters, receipts, marketing CTAs, base64 instructions, password reset notifications, quoted old email content.
6. **Derivation versioning**: `task_derivation_version` stored with each task for safe migration.

---

## Sources

- Ollama API: https://github.com/ollama/ollama/blob/main/docs/api.md
- Gmail API: https://developers.google.com/gmail/api/reference/rest
- Gmail Quota: https://developers.google.com/gmail/api/reference/quota
- FastAPI Lifespan: https://fastapi.tiangolo.com/advanced/events/
- SQLite WAL: https://sqlite.org/wal.html
- SQLite FTS5: https://sqlite.org/fts5.html
- TanStack Query: https://tanstack.com/query/latest/docs
- TanStack Virtual: https://tanstack.com/virtual/latest/docs
- SSE/EventSource: https://developer.mozilla.org/en-US/docs/Web/API/EventSource
