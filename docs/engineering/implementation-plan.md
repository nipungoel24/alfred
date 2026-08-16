# Alfred Engineering Hardening — Implementation Plan

---

## Phase 1: Database Foundation (Commit 1)

### 1.1 SQLite Optimization — `backend/app/db/database.py`

| Current | Target | Why |
|---|---|---|
| Default journal (DELETE) | `PRAGMA journal_mode=WAL` | Concurrent read/write without blocking |
| Default synchronous (FULL) | `PRAGMA synchronous=NORMAL` | Safe in WAL. Reduces fsync overhead |
| No busy_timeout | `PRAGMA busy_timeout=5000` | Prevents SQLITE_BUSY under contention |
| No optimize | `PRAGMA optimize` on connect | Maintains query planner statistics |
| No indexes | Add 6 indexes | SQL-level filtering without full scan |

**New indexes:**
```sql
CREATE INDEX IF NOT EXISTS idx_emails_account_imported ON emails(account_id, imported_at DESC);
CREATE INDEX IF NOT EXISTS idx_emails_thread ON emails(thread_id);
CREATE INDEX IF NOT EXISTS idx_analysis_email ON email_analysis(email_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_source ON tasks(source_email_id);
CREATE INDEX IF NOT EXISTS idx_tasks_thread ON tasks(source_thread_id);
```

### 1.2 Add searchable columns to emails table

Add extracted columns: `sender_col`, `subject_col`, `received_at_col` alongside existing `payload` blob. Enables SQL-level WHERE/ORDER BY without deserializing JSON.

### 1.3 FTS5 search table

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS emails_fts USING fts5(
    email_id UNINDEXED,
    subject,
    sender,
    body,
    content=emails,
    content_rowid=rowid
);
```

### 1.4 Batch commits in repository

Replace individual `self.con.commit()` calls with transaction context manager. Sync imports 50 emails in one transaction.

### 1.5 Jobs table for background work

```sql
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    job_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    priority INTEGER DEFAULT 50,
    status TEXT NOT NULL DEFAULT 'queued',
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 2,
    created_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    error_code TEXT,
    error_message TEXT
);
CREATE INDEX IF NOT EXISTS idx_jobs_status_priority ON jobs(status, priority DESC, created_at ASC);
```

### 1.6 Inference metrics table

```sql
CREATE TABLE IF NOT EXISTS inference_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT,
    model TEXT NOT NULL,
    total_ms REAL,
    load_ms REAL,
    prompt_eval_ms REAL,
    eval_ms REAL,
    prompt_tokens INTEGER,
    output_tokens INTEGER,
    cache_hit INTEGER DEFAULT 0,
    success INTEGER DEFAULT 1,
    recorded_at TEXT NOT NULL
);
```

---

## Phase 2: Backend Service Layer (Commit 2)

### 2.1 Split main.py into routers

| New File | Routes Moved |
|---|---|
| `app/api/routers/accounts.py` | GET /api/accounts, POST /api/accounts/gmail/connect, GET /api/accounts/gmail/callback, DELETE /api/accounts/{id} |
| `app/api/routers/emails.py` | GET /api/emails, GET /api/emails/{id}, POST /api/emails/import, POST /api/emails/{id}/draft |
| `app/api/routers/sync.py` | POST /api/accounts/{id}/sync |
| `app/api/routers/analysis.py` | POST /api/emails/{id}/analyze, POST /api/emails/analyze, GET /api/analysis/progress (SSE) |
| `app/api/routers/tasks.py` | GET /api/tasks, POST /api/tasks/{id}/toggle, DELETE /api/tasks/{id} |
| `app/api/routers/briefing.py` | GET /api/briefing, POST /api/briefing/generate |

### 2.2 Application lifecycle — `app/core/lifecycle.py`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await ollama_client.preload_model(settings.ollama_model)
    analysis_worker.start()
    yield
    # Shutdown
    analysis_worker.stop()
    db.close()
```

### 2.3 Background analysis worker — `app/workers/analysis_worker.py`

- `asyncio.Queue` consumed by a persistent `asyncio.Task`
- Processes jobs from SQLite `jobs` table
- Records inference metrics
- Emits SSE progress events
- Respects concurrency limit (default: 1)
- Implements bounded retry with backoff
- Pauses on repeated Ollama failures

### 2.4 SSE progress endpoint — `app/api/routers/analysis.py`

```python
@router.get('/api/analysis/progress')
async def analysis_progress():
    async def event_stream():
        while True:
            event = await progress_queue.get()
            yield f"data: {json.dumps(event)}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

### 2.5 Decouple sync from analysis

`POST /sync` now:
1. Calls Gmail API
2. Normalizes and stores messages
3. Returns immediately with `{imported: N, synced: true}`
4. Enqueues analysis jobs with priority sorting

---

## Phase 3: Ollama Optimization (Commit 3)

### 3.1 Model preload on startup

Send `{"model": "qwen3:4b", "keep_alive": -1}` during lifespan startup.

### 3.2 keep_alive on every request

Add `"keep_alive": "30m"` to every `/api/generate` payload.

### 3.3 Capture response metrics

Extract `total_duration`, `load_duration`, `prompt_eval_duration`, `prompt_eval_count`, `eval_duration`, `eval_count` from Ollama response. Convert from nanoseconds. Persist to `inference_metrics`.

### 3.4 Error classification

Replace generic `OllamaUnavailable` with:
- `OllamaUnavailable` — service unreachable
- `OllamaTimeout` — request exceeded deadline
- `OllamaInvalidResponse` — malformed JSON
- `OllamaModelMissing` — requested model not found

### 3.5 Prompt optimization

- Truncate email body to 2000 chars for analysis (measure token reduction)
- Strip quoted email history (lines starting with `>`)
- Strip large base64 blocks
- Strip email signatures after `--` delimiter
- Strip tracking pixels and HTML boilerplate
- Measure prompt_token count before/after

---

## Phase 4: Task Derivation Redesign (Commit 4)

### 4.1 TaskDerivationService — `app/services/task_derivation.py`

```python
class TaskDerivationService:
    DERIVATION_VERSION = "2"
    
    def derive_tasks(self, email, analysis) -> list[Task]:
        candidates = []
        for item in analysis.action_items:
            if not self._is_user_actionable(item, email):
                continue
            if self._is_noise(item):
                continue
            candidates.append(self._build_task(item, email, analysis))
        return self._deduplicate(candidates)
```

### 4.2 Ownership validation

Reject tasks where:
- Action is assigned to someone other than the user
- Source is a newsletter/promotional email
- Source is a receipt
- Action is a marketing CTA ("Buy now", "Complete your profile")
- Action involves decoding/verifying credentials
- Action comes from quoted old email content

### 4.3 Task fingerprint for deduplication

```python
def task_fingerprint(thread_id, normalized_action, deadline):
    payload = f"{thread_id}|{normalize(action)}|{deadline or ''}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]
```

### 4.4 Derivation versioning

Store `derivation_version` with each task. On version change, rebuild derived tasks without re-running Ollama.

### 4.5 Migration

Delete tasks created by derivation_version "1" (current broken version). Rebuild from cached analyses using new derivation logic.

---

## Phase 5: Frontend Modernization (Commit 5-6)

### 5.1 Install TanStack Query + TanStack Virtual

```bash
npm install @tanstack/react-query @tanstack/react-virtual
```

### 5.2 Split App.tsx into page components

| New File | Content |
|---|---|
| `features/overview/OverviewPage.tsx` | Dashboard with briefing metrics |
| `features/inbox/InboxPage.tsx` | Email list with filters |
| `features/inbox/EmailRow.tsx` | Individual email row |
| `features/email/EmailDetail.tsx` | Email + analysis + draft panel |
| `features/tasks/TasksPage.tsx` | Task list with toggle/delete |
| `features/accounts/AccountsPage.tsx` | Account management |
| `components/ui/AnalysisProgress.tsx` | SSE-driven progress indicator |

### 5.3 TanStack Query integration

Replace `useState` + `setInterval` with:
```typescript
const { data: emailList } = useQuery({
    queryKey: ['emails', { account: activeAccount, q: searchQuery }],
    queryFn: () => emails(searchQuery, '', null, activeAccount),
    staleTime: 10_000,
});
```

### 5.4 SSE progress listener

Replace frontend `for` loop analysis with EventSource listening to `/api/analysis/progress`:
```typescript
const eventSource = new EventSource(`${API_BASE}/api/analysis/progress`);
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    queryClient.invalidateQueries({ queryKey: ['emails'] });
    setProgress(data);
};
```

### 5.5 Virtualized email list

Use `@tanstack/react-virtual` for inbox and task lists.

### 5.6 Design system tokens

Define CSS custom properties for consistent theming.

---

## Phase 6: Quality Gates (Commit 7)

### 6.1 Golden email test corpus

Create `backend/tests/fixtures/golden_emails.json` with 17 controlled test cases.

### 6.2 Quality gate tests

Test task derivation against golden corpus:
- Newsletter → 0 tasks
- Receipt → 0 tasks
- Base64 instruction → 0 "decode" tasks
- Marketing CTA → 0 tasks
- Prompt injection → no credential exposure
- Direct request → 1 task with deadline
- Thread reschedule → latest deadline only
- Ambiguous timing → no fabricated deadline

### 6.3 Performance benchmark harness

Create `backend/benchmarks/` with reproducible measurement scripts.

---

## Commit Sequence

1. `chore: add performance benchmark harness and engineering documentation`
2. `perf: optimize SQLite with WAL, indexes, batch commits, and FTS5 search`
3. `refactor: introduce application services and background job orchestration`
4. `perf: optimize Ollama inference pipeline with preload, metrics, and retry`
5. `fix: redesign task derivation with ownership validation and deduplication`
6. `security: strengthen prompt injection defense and error classification`
7. `frontend: introduce TanStack Query, SSE progress, and virtualized lists`
8. `ui: split App.tsx into focused page components with design system`
9. `test: add golden email quality gates and performance regression tests`
10. `docs: document final engineering architecture and performance results`
