import csv, io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .db.repositories import Repository
from .mail.normalizer import normalized_email
from .mail.fingerprint import content_fingerprint
from .mail.briefing_fingerprint import briefing_fingerprint, BRIEFING_SCHEMA_VERSION
from .ai.ollama_client import OllamaClient, OllamaUnavailable
from .ai.service import AIService
settings=get_settings(); repo=Repository(settings.database_path); ai=AIService(OllamaClient(settings.ollama_base_url),settings.ollama_model)
app=FastAPI(title='Alfred local API'); app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','tauri://localhost'],allow_methods=['*'],allow_headers=['*'])
@app.exception_handler(OllamaUnavailable)
async def ollama_error(_,e): return JSONResponse(status_code=503,content={'error':{'code':'OLLAMA_UNAVAILABLE','message':str(e),'details':{'model':settings.ollama_model}}})
@app.get('/health')
async def health():
 try: await ai.health(); return {'status':'ok','ai':'ready'}
 except OllamaUnavailable: return {'status':'ok','ai':'unavailable'}
@app.get('/api/config')
def config(): return {'ollama_base_url':settings.ollama_base_url,'ollama_model':settings.ollama_model,'database_path':str(settings.database_path)}
@app.get('/api/emails')
def emails(q:str|None=None, priority:str|None=None, needs_reply:bool|None=None):
 result=repo.emails()
 for e in result: e.analysis=repo.cached_analysis(e.id,content_fingerprint(e),settings.ollama_model)
 if q: result=[e for e in result if q.lower() in (e.subject+' '+e.sender+' '+e.body).lower()]
 if priority: result=[e for e in result if e.analysis and e.analysis.priority.value==priority]
 if needs_reply is not None: result=[e for e in result if e.analysis and e.analysis.needs_reply==needs_reply]
 return result
@app.get('/api/emails/{email_id}')
def email(email_id:str):
 e=repo.email(email_id)
 if not e: return JSONResponse(status_code=404,content={'error':{'code':'EMAIL_NOT_FOUND','message':'Email was not found.','details':{}}})
 e.analysis=repo.cached_analysis(e.id,content_fingerprint(e),settings.ollama_model); return e
@app.post('/api/emails/import')
async def import_csv(file:UploadFile=File(...)):
 text=(await file.read()).decode('utf-8-sig',errors='replace'); rows=list(csv.DictReader(io.StringIO(text))); seen=set(); count=0
 for i,row in enumerate(rows):
  e=normalized_email(row,i)
  if e.id in seen: continue
  seen.add(e.id); repo.upsert_email(e,content_fingerprint(e)); count+=1
 return {'imported':count,'skipped_duplicates':len(rows)-count}
@app.post('/api/emails/{email_id}/analyze')
async def analyze(email_id:str):
 e=repo.email(email_id)
 if not e: return JSONResponse(status_code=404,content={'error':{'code':'EMAIL_NOT_FOUND','message':'Email was not found.','details':{}}})
 fp=content_fingerprint(e); cached=repo.cached_analysis(e.id,fp,settings.ollama_model)
 if cached: return {'analysis':cached,'cached':True}
 analysis=await ai.analyze_email(e); repo.save_analysis(e.id,fp,settings.ollama_model,analysis); return {'analysis':analysis,'cached':False}
@app.post('/api/emails/analyze')
async def analyze_all():
 result=[]
 for e in repo.emails(): result.append(await analyze(e.id))
 return {'processed':len(result),'cached':sum(x['cached'] for x in result)}
@app.post('/api/emails/{email_id}/draft')
async def draft(email_id:str):
 e=repo.email(email_id)
 if not e: return JSONResponse(status_code=404,content={'error':{'code':'EMAIL_NOT_FOUND','message':'Email was not found.','details':{}}})
 return {'draft':await ai.draft_reply(e)}
@app.get('/api/briefing')
async def briefing(): return await generate_briefing()
@app.post('/api/briefing/generate')
async def generate_briefing():
 emails=repo.emails()
 for e in emails: e.analysis=repo.cached_analysis(e.id,content_fingerprint(e),settings.ollama_model)
 fingerprint=briefing_fingerprint(emails,settings.ollama_model)
 cached=repo.cached_briefing(fingerprint,settings.ollama_model,BRIEFING_SCHEMA_VERSION)
 if cached: return cached
 generated=await ai.generate_inbox_briefing(emails)
 repo.save_briefing(fingerprint,settings.ollama_model,generated,BRIEFING_SCHEMA_VERSION)
 return generated
