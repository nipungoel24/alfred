import csv, io, uuid
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .db.repositories import Repository
from .db.secure_store import encrypt_token, decrypt_token
from .mail.normalizer import normalized_email
from .mail.fingerprint import content_fingerprint
from .mail.briefing_fingerprint import briefing_fingerprint, BRIEFING_SCHEMA_VERSION
from .mail.providers.gmail import GmailProvider
from .ai.ollama_client import OllamaClient, OllamaUnavailable
from .ai.service import AIService
from .schemas import Email, EmailAnalysis, InboxBriefing, EmailAccount, Task

settings = get_settings()
repo = Repository(settings.database_path)
ai = AIService(OllamaClient(settings.ollama_base_url), settings.ollama_model)

# Instantiate Gmail provider
gmail_provider = GmailProvider(settings.gmail_client_id, settings.gmail_client_secret)

app = FastAPI(title='Alfred local API')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'tauri://localhost'],
    allow_methods=['*'],
    allow_headers=['*']
)

@app.exception_handler(OllamaUnavailable)
async def ollama_error(_, e):
    return JSONResponse(
        status_code=503,
        content={'error': {'code': 'OLLAMA_UNAVAILABLE', 'message': str(e), 'details': {'model': settings.ollama_model}}}
    )

@app.get('/health')
async def health():
    try:
        await ai.health()
        return {'status': 'ok', 'ai': 'ready'}
    except OllamaUnavailable:
        return {'status': 'ok', 'ai': 'unavailable'}

@app.get('/api/config')
def config():
    return {
        'ollama_base_url': settings.ollama_base_url,
        'ollama_model': settings.ollama_model,
        'database_path': str(settings.database_path)
    }

# --- EMAIL ACCOUNTS ---
@app.get('/api/accounts')
def get_accounts():
    return repo.accounts()

@app.post('/api/accounts/gmail/connect')
async def connect_gmail(redirect_uri: str = Query(...)):
    if settings.gmail_client_id == "PLACEHOLDER_CLIENT_ID" or not settings.gmail_client_id:
        raise HTTPException(
            status_code=400,
            detail="Gmail OAuth credentials are not configured in your .env file."
        )
    auth_url = await gmail_provider.get_auth_url(redirect_uri)
    return {"url": auth_url}

@app.get('/api/accounts/gmail/callback')
async def gmail_callback(code: str = Query(...), state: str | None = None, redirect_uri: str = Query(...)):
    try:
        # Exchange code for tokens
        tokens = await gmail_provider.exchange_code(code, redirect_uri)
        access_token = tokens["access_token"]
        refresh_token = tokens.get("refresh_token", "")
        expires_in = tokens.get("expires_in", 3600)
        
        # Query user profile email
        profile = await gmail_provider.get_user_info(access_token)
        email_address = profile["email"]
        name = profile.get("name", email_address.split("@")[0])
        
        account_id = f"gmail_{email_address}"
        
        # Save credentials securely
        enc_access = encrypt_token(access_token)
        enc_refresh = encrypt_token(refresh_token)
        expires_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat()
        
        account = EmailAccount(
            id=account_id,
            provider="gmail",
            email_address=email_address,
            display_name=name,
            connection_status="connected",
            last_sync_at=None,
            sync_cursor=None
        )
        
        repo.save_account(account)
        repo.save_credentials(account_id, enc_refresh, enc_access, expires_at)
        
        html_content = """
        <html>
        <head>
            <title>Alfred Authorized</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #121214; color: #e1e1e6; text-align: center; padding-top: 100px; }
                h1 { color: #00e676; }
                p { font-size: 1.1em; color: #a9a9b2; }
            </style>
        </head>
        <body>
            <h1>Alfred Successfully Connected!</h1>
            <p>Gmail account authorization was successful. You can close this window now and return to Alfred.</p>
            <script>
                // Post success message to opener if applicable
                if (window.opener) {
                    window.opener.postMessage('auth_success', '*');
                }
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        return HTMLResponse(
            content=f"<html><body><h1>Authentication Failed</h1><p>{str(e)}</p></body></html>",
            status_code=500
        )

@app.post('/api/accounts/{account_id}/sync')
async def sync_account(account_id: str):
    account = repo.account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Email account not found")
        
    creds = repo.credentials(account_id)
    if not creds:
        raise HTTPException(status_code=400, detail="OAuth credentials missing for this account")
        
    # Decrypt token secrets
    access_token = decrypt_token(creds["encrypted_access_token"])
    refresh_token = decrypt_token(creds["encrypted_refresh_token"])
    
    cred_payload = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": creds["expires_at"]
    }
    
    try:
        if account.provider == "gmail":
            res = await gmail_provider.sync_messages(account, cred_payload, repo)
            return res
        else:
            raise HTTPException(status_code=400, detail="Unsupported account provider")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync error: {str(e)}")

@app.delete('/api/accounts/{account_id}')
def delete_account(account_id: str):
    account = repo.account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Email account not found")
    repo.delete_account(account_id)
    return {"status": "deleted"}

# --- EMAILS ---
@app.get('/api/emails')
def get_emails(q: str | None = None, priority: str | None = None, needs_reply: bool | None = None, account_id: str | None = None):
    result = repo.emails(account_id)
    for e in result:
        e.analysis = repo.cached_analysis(e.id, content_fingerprint(e), settings.ollama_model)
    if q:
        result = [e for e in result if q.lower() in (e.subject + ' ' + e.sender + ' ' + e.body).lower()]
    if priority:
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
    count = 0
    for i, row in enumerate(rows):
        e = normalized_email(row, i)
        if e.id in seen:
            continue
        seen.add(e.id)
        repo.upsert_email(e, content_fingerprint(e))
        count += 1
    return {'imported': count, 'skipped_duplicates': len(rows) - count}

@app.post('/api/emails/{email_id}/analyze')
async def analyze(email_id: str):
    e = repo.email(email_id)
    if not e:
        return JSONResponse(status_code=404, content={'error': {'code': 'EMAIL_NOT_FOUND', 'message': 'Email was not found.', 'details': {}}})
    fp = content_fingerprint(e)
    cached = repo.cached_analysis(e.id, fp, settings.ollama_model)
    if cached:
        return {'analysis': cached, 'cached': True}
    analysis = await ai.analyze_email(e)
    repo.save_analysis(e.id, fp, settings.ollama_model, analysis)
    return {'analysis': analysis, 'cached': False}

@app.post('/api/emails/analyze')
async def analyze_all():
    result = []
    for e in repo.emails():
        result.append(await analyze(e.id))
    return {'processed': len(result), 'cached': sum(x['cached'] for x in result)}

@app.post('/api/emails/{email_id}/draft')
async def draft(email_id: str):
    e = repo.email(email_id)
    if not e:
        return JSONResponse(status_code=404, content={'error': {'code': 'EMAIL_NOT_FOUND', 'message': 'Email was not found.', 'details': {}}})
    
    # Extract bounding thread history
    thread_emails = []
    if e.thread_id:
        all_emails = repo.emails()
        thread_emails = [x for x in all_emails if x.thread_id == e.thread_id]
        
    draft_reply_text = await ai.draft_reply(e, thread_emails)
    return {'draft': draft_reply_text}

# --- BRIEFINGS ---
@app.get('/api/briefing')
async def briefing():
    return await generate_briefing()

@app.post('/api/briefing/generate')
async def generate_briefing():
    emails = repo.emails()
    for e in emails:
        e.analysis = repo.cached_analysis(e.id, content_fingerprint(e), settings.ollama_model)
    fingerprint = briefing_fingerprint(emails, settings.ollama_model)
    cached = repo.cached_briefing(fingerprint, settings.ollama_model, BRIEFING_SCHEMA_VERSION)
    if cached:
        return cached
    generated = await ai.generate_inbox_briefing(emails)
    repo.save_briefing(fingerprint, settings.ollama_model, generated, BRIEFING_SCHEMA_VERSION)
    return generated

# --- TASKS ---
@app.get('/api/tasks')
def get_tasks():
    return repo.tasks()

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
