# Alfred Architecture Audit — Current State

*Prepared: August 2026*

---

## Module Map

| Module | File | Lines | Responsibility |
|---|---|---|---|
| **main.py** | `backend/app/main.py` | 304 | ALL routes, OAuth, PKCE, sync orchestration, analysis, briefing, task CRUD, error handling |
| **config.py** | `backend/app/config.py` | 29 | Settings with dotenv loading |
| **schemas.py** | `backend/app/schemas.py` | 57 | ALL Pydantic models (Email, Analysis, Briefing, Account, Task) |
| **ollama_client.py** | `backend/app/ai/ollama_client.py` | 18 | HTTP client for Ollama `/api/generate` |
| **service.py** | `backend/app/ai/service.py` | 51 | AI analysis, draft generation, briefing generation |
| **database.py** | `backend/app/db/database.py` | 78 | Schema DDL, connection factory, migrations |
| **repositories.py** | `backend/app/db/repositories.py` | 204 | ALL data access + task derivation side effects |
| **secure_store.py** | `backend/app/db/secure_store.py` | 62 | DPAPI encrypt/decrypt |
| **gmail.py** | `backend/app/mail/providers/gmail.py` | 347 | OAuth, token refresh, sync, message normalization, HTML sanitization |
| **normalizer.py** | `backend/app/mail/normalizer.py` | 22 | CSV import normalization |
| **fingerprint.py** | `backend/app/mail/fingerprint.py` | 7 | Content hash for analysis cache key |
| **briefing_fingerprint.py** | `backend/app/mail/briefing_fingerprint.py` | 12 | Briefing cache key |
| **App.tsx** | `frontend/src/App.tsx` | 723 | ALL pages, ALL state, ALL handlers, ALL rendering |
| **emails.ts** | `frontend/src/api/emails.ts` | 103 | API client + type definitions |
| **client.ts** | `frontend/src/api/client.ts` | ~10 | Base fetch wrapper |
| **styles.css** | `frontend/src/styles.css` | ~200 | All CSS |

---

## Critical Findings

### F1: Monolithic main.py (SEVERITY: HIGH)

**Problem**: 304-line file contains 15 route handlers, OAuth state management, PKCE generation, sync orchestration, analysis invocation, briefing generation, and all CRUD. Every concern is tangled.

**Impact**: Impossible to test individual concerns. Changes to OAuth risk breaking analysis. Changes to sync risk breaking tasks.

**Fix**: Split into routers: `accounts.py`, `emails.py`, `sync.py`, `analysis.py`, `tasks.py`, `briefing.py`.

---

### F2: Sync blocks on analysis (SEVERITY: CRITICAL)

**Problem**: `POST /api/accounts/{id}/sync` calls Gmail sync, then the FRONTEND runs a sequential `for` loop calling `POST /api/emails/{id}/analyze` for each unanalyzed email. The entire UI is blocked during this process.

**Evidence**: `App.tsx` lines 92-107:
```typescript
for (let i = 0; i < unanalyzed.length; i++) {
  setSyncProgress(`Analyzing message ${i + 1} of ${unanalyzed.length} locally...`);
  await analyze(unanalyzed[i].id);
}
```

**Impact**: 50 emails × ~1s/email = 50+ seconds of blocked UI. User sees "Analyzing message 35 of 50 locally..." and cannot navigate, search, or interact.

**Fix**: Backend async worker queue. Sync returns immediately. Analysis runs in background. SSE pushes progress to frontend.

---

### F3: Task derivation as save_analysis() side effect (SEVERITY: CRITICAL)

**Problem**: `repositories.py` lines 51-85 create tasks inside `save_analysis()`. Every `action_item` and every `deadline` from AI output becomes a `Task` row unconditionally. No validation, no ownership check, no confidence threshold.

**Evidence**: 50 emails → 91 tasks including:
- "Decode the base64 string to reveal the actual content."
- "Verify the user's TikTok account credentials."
- "Check if the user has a pending password reset request."

**Impact**: Task list is unusable. Users lose trust in Alfred's intelligence.

**Fix**: Extract `TaskDerivationService`. Validate ownership. Add confidence threshold. Deduplicate. Version derivation.

---

### F4: No database optimization (SEVERITY: HIGH)

**Problem**: Default SQLite configuration. No WAL, no indexes, individual commits after every operation.

**Evidence**:
- `database.py`: No PRAGMA settings for WAL, synchronous, or busy_timeout.
- `repositories.py`: `self.con.commit()` called 8 times across methods. Each email upsert = 1 commit. 50 emails = 50 commits.
- No indexes on `account_id`, `thread_id`, `imported_at`.

**Impact**: Slow sync on mechanical drives. Reader-writer contention. O(N) queries for filtered email lists.

---

### F5: In-Python email filtering (SEVERITY: HIGH)

**Problem**: `GET /api/emails` loads ALL emails from DB, deserializes ALL JSON payloads, then filters in Python.

**Evidence**: `main.py` lines 194-205:
```python
result = repo.emails(account_id)
for e in result:
    e.analysis = repo.cached_analysis(e.id, content_fingerprint(e), settings.ollama_model)
if q:
    result = [e for e in result if q.lower() in (e.subject + ' ' + e.sender + ' ' + e.body).lower()]
```

**Impact**: For 1000 emails: load 1000 JSON blobs + deserialize 1000 Pydantic models + run 1000 fingerprint hashes + load 1000 analysis records + do string search across all. O(N²) behavior.

---

### F6: Frontend polling storm (SEVERITY: MEDIUM)

**Problem**: 10-second polling interval fetches ALL data (accounts + tasks + emails + briefing) every 10 seconds regardless of whether anything changed.

**Evidence**: `App.tsx` lines 74-81:
```typescript
const interval = setInterval(() => { load(); }, 10000);
```

Where `load()` calls 4 API endpoints sequentially.

**Impact**: Unnecessary network traffic. Unnecessary deserialization. Stale data for up to 10 seconds. No real-time progress during analysis.

---

### F7: 723-line monolithic App.tsx (SEVERITY: HIGH)

**Problem**: Single component contains all pages (Overview, Inbox, Important, Needs Reply, Tasks, Deadlines, Later, Accounts, Settings), all state (emails, briefing, accounts, tasks, sync status, filters, draft), all handlers (sync, analyze, connect, disconnect, toggle, delete, draft).

**Impact**: Any change risks affecting all pages. Impossible to lazy-load pages. All state re-renders all pages.

---

### F8: No error classification (SEVERITY: MEDIUM)

**Problem**: One Ollama inference failure shows global error banner. All errors treated identically.

**Evidence**: User saw `"Ollama inference failed."` as a global banner while analysis actually continued for remaining messages.

**Fix**: Typed error codes. Scoped error display. Per-item retry.

---

### F9: gmail_raw storage bloat (SEVERITY: MEDIUM)

**Problem**: `source_metadata: {"gmail_raw": detail}` stores the entire Gmail API response for every email. A single email's raw response can be 50-100KB+ with HTML body and attachment metadata.

**Evidence**: `gmail.py` line 297: `source_metadata={"gmail_raw": detail}`

**Impact**: 1000 emails × 75KB = ~75MB of redundant raw storage when normalized fields are already extracted.

---

### F10: No application lifecycle management (SEVERITY: MEDIUM)

**Problem**: No `lifespan` context manager. Resources created at module level. No model preload. No graceful shutdown. No worker cleanup.

---

## Dependency Graph

```
main.py
├── config.py
├── repositories.py
│   ├── database.py
│   └── schemas.py
├── secure_store.py
├── normalizer.py
├── fingerprint.py
├── briefing_fingerprint.py
├── gmail.py
│   ├── base.py
│   ├── schemas.py
│   └── fingerprint.py (imports from parent)
├── ollama_client.py
├── service.py (AI)
│   ├── ollama_client.py
│   └── schemas.py
└── schemas.py

App.tsx
├── api/emails.ts
│   └── api/client.ts
├── components/PriorityBadge.tsx
└── styles.css
```

**Circular risks**: `gmail.py` imports from `...schemas`, `...mail.fingerprint`. Repository imports from `..schemas`. No actual circular imports, but tight coupling through schemas.

---

## N+1 Query Patterns

1. **`GET /api/emails`**: For each email, calls `repo.cached_analysis()` individually. N emails = N+1 queries.
2. **`save_analysis()`**: Calls `self.email(email_id)` to re-fetch the email just saved. Then calls `self.task()` for each action_item to check existence. M action_items = M+1 queries.
3. **Draft generation**: `repo.emails()` fetches ALL emails to find thread members. Should query by `thread_id`.

---

## Security Observations

- ✓ DPAPI token encryption on Windows
- ✓ Prompt injection defense in system prompt
- ✓ HTML sanitization strips scripts/event handlers
- ✗ OAuth callback exception handler reflects error message to HTML (potential XSS in error path)
- ✗ `OAUTH_STATES` is in-memory dict with no TTL. Memory leak if states are never consumed.
- ✗ CORS allows `*` headers — acceptable for local desktop but should be tightened in production config.
