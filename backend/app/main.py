"""Alfred local FastAPI application.

Routes are organized here for simplicity. The architecture separates:
- Routes (this file): HTTP request/response handling
- Services: Business logic (AI analysis, task derivation)
- Infrastructure: External system clients (Ollama, Gmail)
- Repository: Data access layer
"""
import csv, io, uuid, secrets, hashlib, base64, json, asyncio, logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Request
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .db.repositories import Repository
from .db.secure_store import encrypt_token, decrypt_token
from .mail.normalizer import normalized_email
from .mail.fingerprint import content_fingerprint
from .mail.briefing_fingerprint import briefing_fingerprint, BRIEFING_SCHEMA_VERSION
from .mail.providers.gmail import GmailProvider
from .mail.eligibility import MailEligibilityPolicy, GmailCategory
from .ai.ollama_client import OllamaClient, OllamaUnavailable, OllamaTimeout, OllamaInvalidResponse, OllamaModelMissing
from .ai.service import AIService
from .services.task_derivation import derive_tasks, rebuild_tasks_from_analyses, DERIVATION_VERSION
from .schemas import Email, EmailAnalysis, InboxBriefing, EmailAccount, Task

settings = get_settings()
logger = logging.getLogger("alfred.oauth")

# ── Shared state ──
repo = Repository(settings.database_path)
ollama_client = OllamaClient(settings.ollama_base_url)
ai = AIService(ollama_client, settings.ollama_model)
gmail_provider = GmailProvider(settings.gmail_client_id, settings.gmail_client_secret)

OAUTH_STATES = {}  # state -> {"verifier": verifier, "redirect_uri": redirect_uri}

# ── Analysis progress events (SSE) ──
progress_subscribers: list[asyncio.Queue] = []

def _broadcast_progress(event: dict):
    """Send a progress event to all SSE subscribers."""
    for q in progress_subscribers:
        try:
            q.put_nowait(event)
        except asyncio.QueueFull:
            pass


# ── Background analysis worker ──
_worker_task: asyncio.Task | None = None
_worker_running = False
WORKER_CONCURRENCY = 1

async def _analysis_worker():
    """Background worker that processes analysis jobs from SQLite."""
    global _worker_running
    _worker_running = True
    consecutive_failures = 0
    max_consecutive_failures = 5

    while _worker_running:
        job = repo.next_job('analyze_email')
        if not job:
            await asyncio.sleep(1.0)
            continue
            
        job_id = job['id']
        email_id = job['target_id']
        
        # Mark as running
        repo.update_job_status(job_id, 'running')
        
        e = repo.email(email_id)
        if not e:
            repo.update_job_status(job_id, 'failed', error_message='Email not found')
            continue

        # Eligibility guard: a message that became spam/trash/archived after
        # enqueueing must not be analyzed by the background queue. Reads the
        # persisted projection (source of truth at runtime).
        persisted = repo.email_eligibility(email_id)
        if not persisted or persisted['pipeline_eligibility'] == 'excluded':
            repo.update_job_status(job_id, 'cancelled', error_message='Email no longer pipeline-eligible')
            _broadcast_progress({
                "type": "analysis_cancelled", "email_id": e.id,
                "pending": repo.pending_job_count('analyze_email')
            })
            continue

        fp = content_fingerprint(e)
        cached = repo.cached_analysis(e.id, fp, settings.ollama_model)
        if cached:
            # Already analyzed, derive tasks and skip
            _derive_and_save_tasks(e, cached)
            repo.update_job_status(job_id, 'succeeded')
            _broadcast_progress({
                "type": "analysis_complete", "email_id": e.id, "cached": True,
                "pending": repo.pending_job_count('analyze_email')
            })
            consecutive_failures = 0
            continue

        try:
            analysis, metrics = await ai.analyze_email(e)
            repo.save_analysis(e.id, fp, settings.ollama_model, analysis)

            # Record inference metrics
            repo.record_inference_metric(
                job_id=job_id, model=settings.ollama_model,
                total_ms=metrics.total_ms, load_ms=metrics.load_ms,
                prompt_eval_ms=metrics.prompt_eval_ms, eval_ms=metrics.eval_ms,
                prompt_tokens=metrics.prompt_tokens, output_tokens=metrics.output_tokens,
                cache_hit=False, success=True
            )

            # Derive tasks from analysis
            _derive_and_save_tasks(e, analysis)
            
            repo.update_job_status(job_id, 'succeeded')

            _broadcast_progress({
                "type": "analysis_complete", "email_id": e.id, "cached": False,
                "pending": repo.pending_job_count('analyze_email'),
                "total_ms": round(metrics.total_ms, 1),
            })
            consecutive_failures = 0

        except (OllamaUnavailable, OllamaTimeout) as ex:
            consecutive_failures += 1
            repo.update_job_status(job_id, 'retryable_failed', error_code=type(ex).__name__, error_message=str(ex))
            _broadcast_progress({
                "type": "analysis_error", "email_id": e.id,
                "error": type(ex).__name__,
                "pending": repo.pending_job_count('analyze_email'),
            })
            if consecutive_failures >= max_consecutive_failures:
                _broadcast_progress({
                    "type": "worker_paused",
                    "reason": f"Ollama unavailable after {max_consecutive_failures} consecutive failures",
                    "pending": repo.pending_job_count('analyze_email'),
                })
                # Wait before retrying
                await asyncio.sleep(30)
                consecutive_failures = 0

        except (OllamaInvalidResponse, OllamaModelMissing) as ex:
            repo.update_job_status(job_id, 'failed', error_code=type(ex).__name__, error_message=str(ex))
            _broadcast_progress({
                "type": "analysis_error", "email_id": e.id,
                "error": type(ex).__name__,
                "pending": repo.pending_job_count('analyze_email'),
            })

        except Exception as ex:
            repo.update_job_status(job_id, 'failed', error_code='UNKNOWN', error_message=str(ex))
            _broadcast_progress({
                "type": "analysis_error", "email_id": e.id,
                "error": "UNKNOWN",
                "pending": repo.pending_job_count('analyze_email'),
            })


def _derive_and_save_tasks(email: Email, analysis: EmailAnalysis):
    """Derive tasks from analysis and persist them, deduplicating.

    Excluded source mail (spam/trash/archived) never produces new tasks —
    the guard also covers mid-analysis label transitions.
    """
    persisted = repo.email_eligibility(email.id)
    if not persisted or persisted['pipeline_eligibility'] == 'excluded':
        return
    tasks = derive_tasks(email, analysis)
    new_tasks = []
    for t in tasks:
        fp = getattr(t, 'fingerprint', None)
        if fp and repo.task_exists_by_fingerprint(fp):
            continue
        new_tasks.append(t)
    if new_tasks:
        repo.save_tasks_batch(new_tasks)


def generate_pkce_pair():
    verifier = secrets.token_urlsafe(64)
    sha256_hash = hashlib.sha256(verifier.encode('ascii')).digest()
    challenge = base64.urlsafe_b64encode(sha256_hash).decode('ascii').replace('=', '')
    return verifier, challenge


# ── Lifespan ──
async def _label_backfill():
    """Refresh Gmail labels for cached rows missing mailbox state.

    Uses format=METADATA only — no body transfers. Runs once per startup,
    opportunistically, without blocking the API.
    """
    try:
        pending = repo.emails_missing_labels()
        if not pending:
            return
        gmail_accounts = [a for a in repo.accounts()
                          if a.provider == 'gmail' and a.connection_status == 'connected']
        if not gmail_accounts:
            return
        account = gmail_accounts[0]
        creds = repo.credentials(account.id)
        if not creds:
            return
        access_token = decrypt_token(creds['encrypted_access_token'])
        refreshed = 0
        for msg_id in pending:
            labels = await gmail_provider.refresh_message_labels(access_token, msg_id)
            if labels is not None and repo.update_email_labels(msg_id, labels):
                refreshed += 1
        if refreshed:
            print(f"[Alfred] Backfilled Gmail labels for {refreshed} cached messages")
    except Exception:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _worker_task, _worker_running

    # Startup: preload model and start worker
    try:
        await ai.preload()
    except Exception:
        pass  # Non-fatal: first inference will be slower

    # Rebuild tasks from cached analyses if needed (migration from v1 to v2)
    try:
        rebuilt = rebuild_tasks_from_analyses(repo, settings.ollama_model)
        if rebuilt > 0:
            print(f"[Alfred] Rebuilt {rebuilt} tasks with derivation v{DERIVATION_VERSION}")
            
        # Reset any stuck 'running' jobs to 'queued' on startup
        repo.con.execute('UPDATE jobs SET status="queued" WHERE status="running"')
        repo.reset_retryable_jobs()
        repo.con.commit()
    except Exception:
        pass

    # Start background analysis worker
    _worker_task = asyncio.create_task(_analysis_worker())

    # Backfill Gmail labels for legacy rows (non-blocking, metadata only)
    backfill_task = asyncio.create_task(_label_backfill())

    yield

    # Shutdown
    _worker_running = False
    if _worker_task:
        _worker_task.cancel()
        try:
            await _worker_task
        except asyncio.CancelledError:
            pass
    backfill_task.cancel()
    repo.close()


app = FastAPI(title='Alfred local API', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173', 'tauri://localhost'],
    allow_methods=['*'],
    allow_headers=['*']
)


# ── Error handlers ──
@app.exception_handler(OllamaUnavailable)
async def ollama_unavailable_handler(_, e):
    return JSONResponse(
        status_code=503,
        content={'error': {'code': 'OLLAMA_UNAVAILABLE', 'message': str(e), 'details': {'model': settings.ollama_model}}}
    )

@app.exception_handler(OllamaTimeout)
async def ollama_timeout_handler(_, e):
    return JSONResponse(
        status_code=504,
        content={'error': {'code': 'OLLAMA_TIMEOUT', 'message': str(e), 'details': {'model': settings.ollama_model}}}
    )

@app.exception_handler(OllamaInvalidResponse)
async def ollama_invalid_handler(_, e):
    return JSONResponse(
        status_code=502,
        content={'error': {'code': 'OLLAMA_INVALID_RESPONSE', 'message': str(e), 'details': {'model': settings.ollama_model}}}
    )

@app.exception_handler(OllamaModelMissing)
async def ollama_model_missing_handler(_, e):
    return JSONResponse(
        status_code=503,
        content={'error': {'code': 'OLLAMA_MODEL_MISSING', 'message': str(e), 'details': {'model': settings.ollama_model}}}
    )


# ── Health & Config ──
@app.get('/health')
async def health():
    try:
        await ai.health()
        return {'status': 'ok', 'ai': 'ready'}
    except (OllamaUnavailable, OllamaTimeout):
        return {'status': 'ok', 'ai': 'unavailable'}

@app.get('/api/config')
def config():
    return {
        'ollama_base_url': settings.ollama_base_url,
        'ollama_model': settings.ollama_model,
        'database_path': str(settings.database_path)
    }


# ── Accounts ──
@app.get('/api/accounts')
def get_accounts():
    accounts = repo.accounts()
    result = []
    for acc in accounts:
        entry = acc.model_dump(mode='json')
        # Derived backfill status for progressive All Mail sync (frontend
        # polls /backfill while incomplete).
        backfill_complete = False
        try:
            cursor = json.loads(acc.sync_cursor) if acc.sync_cursor else {}
            backfill_complete = bool(cursor.get("backfill_complete"))
        except Exception:
            pass
        entry["backfill_complete"] = backfill_complete
        result.append(entry)
    return result

@app.post('/api/accounts/gmail/connect')
async def connect_gmail(redirect_uri: str = Query(...)):
    if settings.gmail_client_id == "PLACEHOLDER_CLIENT_ID" or not settings.gmail_client_id:
        raise HTTPException(
            status_code=400,
            detail="Gmail OAuth credentials are not configured in your .env file."
        )
    state = uuid.uuid4().hex
    verifier, challenge = generate_pkce_pair()
    OAUTH_STATES[state] = {
        "verifier": verifier,
        "redirect_uri": redirect_uri
    }
    auth_url = await gmail_provider.get_auth_url(redirect_uri, state, challenge)
    return {"url": auth_url}

def _oauth_callback_page(success: bool) -> HTMLResponse:
    title = "Gmail connected" if success else "Couldn't connect Gmail"
    message = (
        "You can close this window and return to Alfred."
        if success else "Alfred couldn't complete Google authorization. Return to Alfred and try again."
    )
    accent = "#5bd6a0" if success else "#f28b82"
    status = 200 if success else 400
    return HTMLResponse(content=f'''<!doctype html><html><head><meta charset="utf-8"><title>Alfred</title>
    <style>body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#080a12;color:#eaecf5;font:15px "Segoe UI",system-ui,sans-serif}}main{{width:min(440px,calc(100% - 48px));padding:40px;border:1px solid rgba(255,255,255,.1);border-radius:16px;background:rgba(20,24,38,.92);box-shadow:0 18px 48px rgba(0,0,0,.42)}}.brand{{font-weight:800;letter-spacing:.14em;font-size:14px}}.dot{{width:9px;height:9px;border-radius:50%;background:{accent};display:inline-block;margin-right:8px}}h1{{margin:22px 0 10px;font-size:28px}}p{{margin:0;color:#b0b5cc;line-height:1.55}}a{{display:inline-block;margin-top:28px;padding:9px 14px;border-radius:7px;background:#7c6cf2;color:white;text-decoration:none;font-weight:600}}</style></head>
    <body><main><div class="brand">ALFRED</div><h1><span class="dot"></span>{title}</h1><p>{message}</p><a href="http://localhost:5173">Return to Alfred</a></main>
    <script>if ({str(success).lower()} && window.opener) window.opener.postMessage('auth_success', '*');</script></body></html>''', status_code=status)


@app.get('/api/accounts/gmail/callback')
async def gmail_callback(code: str | None = Query(None), state: str | None = Query(None), redirect_uri: str | None = Query(None), error: str | None = Query(None)):
    if error:
        logger.warning("oauth_authorization_denied")
        return _oauth_callback_page(False)
    if not code or not state:
        logger.warning("oauth_state_missing")
        return _oauth_callback_page(False)
    state_data = OAUTH_STATES.pop(state, None)
    if not state_data:
        logger.warning("oauth_state_invalid")
        return _oauth_callback_page(False)
    actual_redirect = redirect_uri or state_data["redirect_uri"]
    verifier = state_data["verifier"]

    stage = "token_exchange_failed"
    try:
        tokens = await gmail_provider.exchange_code(code, actual_redirect, verifier)
        access_token = tokens["access_token"]
        refresh_token = tokens.get("refresh_token", "")
        expires_in = tokens.get("expires_in", 3600)

        stage = "profile_request_failed"
        profile = await gmail_provider.get_user_info(access_token)
        email_address = profile["email"]
        name = profile.get("name", email_address.split("@")[0])

        account_id = f"gmail_{email_address}"

        enc_access = encrypt_token(access_token)
        enc_refresh = encrypt_token(refresh_token)
        expires_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat()

        account = EmailAccount(
            id=account_id, provider="gmail", email_address=email_address,
            display_name=name, connection_status="connected",
            last_sync_at=None, sync_cursor=None
        )

        repo.save_account(account)
        repo.save_credentials(account_id, enc_refresh, enc_access, expires_at)

        return _oauth_callback_page(True)
    except Exception as exc:
        logger.warning("oauth_%s: %s", stage, type(exc).__name__)
        return _oauth_callback_page(False)

@app.delete('/api/accounts/{account_id}')
def delete_account(account_id: str):
    account = repo.account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Email account not found")
    repo.delete_account(account_id)
    return {"status": "deleted"}


# ── Sync ──
@app.post('/api/accounts/{account_id}/sync')
async def sync_account(account_id: str, load_older: bool = Query(False)):
    account = repo.account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Email account not found")

    creds = repo.credentials(account_id)
    if not creds:
        raise HTTPException(status_code=400, detail="OAuth credentials missing for this account")

    access_token = decrypt_token(creds["encrypted_access_token"])
    refresh_token = decrypt_token(creds["encrypted_refresh_token"])

    cred_payload = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": creds["expires_at"]
    }

    try:
        if account.provider == "gmail":
            res = await gmail_provider.sync_messages(account, cred_payload, repo, load_older=load_older)

            # Enqueue analysis jobs for unanalyzed eligible emails (non-blocking)
            enqueued = 0
            candidates = repo.eligible_emails_without_analysis(settings.ollama_model, account_id=account.id)
            for e in candidates:
                # Central policy: scheduling order (not final priority) and
                # lazy low-value categories.
                if not MailEligibilityPolicy.should_schedule_analysis(e.label_ids):
                    continue
                fp = content_fingerprint(e)
                if repo.cached_analysis(e.id, fp, settings.ollama_model):
                    continue
                prio = MailEligibilityPolicy.analysis_queue_priority(
                    e.label_ids, unread=MailEligibilityPolicy.is_unread(e.label_ids)
                )
                repo.enqueue_job(f"analyze_{e.id}", 'analyze_email', e.id, priority=prio)
                enqueued += 1
            res["analysis_enqueued"] = enqueued

            # Notify worker to wake up (via progress mechanism or sleep cycle)
            _broadcast_progress({"type": "jobs_enqueued", "count": enqueued, "pending": repo.pending_job_count('analyze_email')})

            return res
        else:
            raise HTTPException(status_code=400, detail="Unsupported account provider")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync error: {str(e)}")


@app.post('/api/accounts/{account_id}/backfill')
async def backfill_account(account_id: str):
    """Progressive All Mail backfill — ONE page per call.

    Pages through archived/sent Gmail mail (never spam/trash/drafts) and
    persists the backfill page token in the sync cursor, so restarts
    resume cleanly. Does not enqueue analysis for archived messages and
    never blocks the UI or the AI queue.
    """
    account = repo.account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Email account not found")

    creds = repo.credentials(account_id)
    if not creds:
        raise HTTPException(status_code=400, detail="OAuth credentials missing for this account")

    access_token = decrypt_token(creds["encrypted_access_token"])
    refresh_token = decrypt_token(creds["encrypted_refresh_token"])

    cred_payload = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": creds["expires_at"]
    }

    try:
        if account.provider == "gmail":
            return await gmail_provider.backfill_messages(account, cred_payload, repo)
        else:
            raise HTTPException(status_code=400, detail="Unsupported account provider")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backfill error: {str(e)}")


# ── Analysis Progress (SSE) ──
@app.get('/api/analysis/progress')
async def analysis_progress():
    """Server-Sent Events endpoint for real-time analysis progress."""
    q: asyncio.Queue = asyncio.Queue(maxsize=100)
    progress_subscribers.append(q)

    async def event_stream():
        try:
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'pending': analysis_queue.qsize()})}\n\n"
            while True:
                try:
                    event = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield f"data: {json.dumps({'type': 'heartbeat', 'pending': analysis_queue.qsize()})}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            progress_subscribers.remove(q)

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get('/api/analysis/status')
def analysis_status():
    """Get current analysis queue status."""
    return {
        "pending": analysis_queue.qsize(),
        "worker_running": _worker_running,
    }


# ── Emails ──
VALID_CATEGORIES = {c.value for c in GmailCategory}

@app.get('/api/emails/counts')
def get_email_counts(account_id: str | None = None):
    """Live category + mailbox-state counts (DB-derived, never hardcoded)."""
    return repo.email_counts(account_id)


@app.get('/api/emails')
def get_emails(q: str | None = None, priority: str | None = None, needs_reply: bool | None = None,
               account_id: str | None = None, category: str | None = None,
               scope: str = 'inbox', limit: int = 200, offset: int = 0):
    if category is not None and category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Unknown category: {category}")
    if scope not in ('inbox', 'all'):
        raise HTTPException(status_code=400, detail=f"Unknown scope: {scope}")

    # DB-driven filtering: scope + eligibility + search context.
    # scope=all includes archived mail but NOT spam/trash/draft/sent-only;
    # category tabs apply only to the inbox scope.
    result = repo.emails_filtered(
        account_id=account_id, category=category if scope == 'inbox' else None,
        query=q, scope=scope,
        include_excluded=False, limit=limit, offset=offset
    )

    # Attach cached analyses
    for e in result:
        e.analysis = repo.cached_analysis(e.id, content_fingerprint(e), settings.ollama_model)

    # Apply semantic filters on top of the already-eligible window.
    # 'high' means Important: urgent AND high both qualify.
    if priority:
        if priority == 'high':
            result = [e for e in result if e.analysis
                      and e.analysis.priority.value in ('high', 'urgent')]
        else:
            result = [e for e in result if e.analysis and e.analysis.priority.value == priority]
    if needs_reply is not None:
        result = [e for e in result if e.analysis and e.analysis.needs_reply == needs_reply]
    return result

@app.get('/api/emails/{email_id}')
def get_email(email_id: str):
    e = repo.email(email_id)
    if not e:
        return JSONResponse(status_code=404, content={'error': {'code': 'EMAIL_NOT_FOUND', 'message': 'Email was not found.', 'details': {}}})
    e.analysis = repo.cached_analysis(e.id, content_fingerprint(e), settings.ollama_model)
    return e

@app.post('/api/emails/import')
async def import_csv(file: UploadFile = File(...)):
    text = (await file.read()).decode('utf-8-sig', errors='replace')
    rows = list(csv.DictReader(io.StringIO(text)))
    seen = set()
    batch = []
    for i, row in enumerate(rows):
        e = normalized_email(row, i)
        if e.id in seen:
            continue
        seen.add(e.id)
        batch.append((e, content_fingerprint(e)))

    if batch:
        repo.upsert_emails_batch(batch)

    return {'imported': len(batch), 'skipped_duplicates': len(rows) - len(batch)}

@app.post('/api/emails/{email_id}/analyze')
async def analyze(email_id: str):
    e = repo.email(email_id)
    if not e:
        return JSONResponse(status_code=404, content={'error': {'code': 'EMAIL_NOT_FOUND', 'message': 'Email was not found.', 'details': {}}})
    # User-requested analysis: allowed for active + deferred (opened promo/
    # social); refused for excluded (spam/trash/draft/sent/archived).
    persisted = repo.email_eligibility(email_id)
    if not persisted or persisted['pipeline_eligibility'] == 'excluded':
        return JSONResponse(status_code=409, content={
            'error': {'code': 'EMAIL_EXCLUDED', 'message': 'This message is no longer part of the active inbox and is not analyzed.', 'details': {}}
        })
    fp = content_fingerprint(e)
    cached = repo.cached_analysis(e.id, fp, settings.ollama_model)
    if cached:
        return {'analysis': cached, 'cached': True}

    analysis, metrics = await ai.analyze_email(e)
    repo.save_analysis(e.id, fp, settings.ollama_model, analysis)

    # Derive tasks
    _derive_and_save_tasks(e, analysis)

    return {'analysis': analysis, 'cached': False}

@app.post('/api/emails/analyze')
async def analyze_all():
    """Enqueue all eligible unanalyzed emails for background analysis."""
    enqueued = 0
    candidates = repo.eligible_emails_without_analysis(settings.ollama_model)
    for e in candidates:
        if not MailEligibilityPolicy.should_schedule_analysis(e.label_ids):
            continue
        fp = content_fingerprint(e)
        if repo.cached_analysis(e.id, fp, settings.ollama_model):
            continue
        prio = MailEligibilityPolicy.analysis_queue_priority(
            e.label_ids, unread=MailEligibilityPolicy.is_unread(e.label_ids)
        )
        repo.enqueue_job(f"analyze_{e.id}", 'analyze_email', e.id, priority=prio)
        enqueued += 1
    return {'enqueued': enqueued, 'message': 'Analysis jobs queued for background processing.'}

@app.post('/api/emails/{email_id}/draft')
async def draft(email_id: str):
    e = repo.email(email_id)
    if not e:
        return JSONResponse(status_code=404, content={'error': {'code': 'EMAIL_NOT_FOUND', 'message': 'Email was not found.', 'details': {}}})

    # Use efficient thread query instead of loading all emails
    thread_emails = []
    if e.thread_id:
        thread_emails = repo.emails_by_thread(e.thread_id)

    draft_reply_text = await ai.draft_reply(e, thread_emails)
    return {'draft': draft_reply_text}


# ── Briefings ──
def _briefing_eligible_emails() -> list[Email]:
    """One authoritative briefing candidate set: active inbox, not spam/
    trash/draft/sent-only, promo/social only with strong attention signals.
    """
    emails = repo.emails_filtered(include_excluded=False, limit=1000)
    for e in emails:
        e.analysis = repo.cached_analysis(e.id, content_fingerprint(e), settings.ollama_model)
    result = []
    for e in emails:
        if MailEligibilityPolicy.should_include_in_briefing(
            e.label_ids,
            analysis_priority=e.analysis.priority.value if e.analysis else None,
            needs_reply=e.analysis.needs_reply if e.analysis else None,
        ):
            result.append(e)
    return result


@app.get('/api/briefing')
async def briefing_get():
    return await generate_briefing(force=False)

@app.post('/api/briefing/generate')
async def generate_briefing(force: bool = True):
    emails = _briefing_eligible_emails()
    fingerprint = briefing_fingerprint(emails, settings.ollama_model)
    cached = repo.cached_briefing(fingerprint, settings.ollama_model, BRIEFING_SCHEMA_VERSION)
    if cached and not force:
        return cached
    generated = await ai.generate_inbox_briefing(emails)
    repo.save_briefing(fingerprint, settings.ollama_model, generated, BRIEFING_SCHEMA_VERSION)
    return generated


# ── Tasks ──
@app.get('/api/tasks')
def get_tasks():
    """Active projection: derived tasks whose source email is excluded are
    hidden here but their rows are preserved."""
    return repo.active_tasks()

@app.post('/api/tasks/{task_id}/toggle')
def toggle_task(task_id: str):
    t = repo.task(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    t.status = 'completed' if t.status == 'pending' else 'pending'
    repo.save_task(t)
    return t

@app.delete('/api/tasks/{task_id}')
def delete_task(task_id: str):
    t = repo.task(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    repo.delete_task(task_id)
    return {"status": "deleted"}
