import sys; sys.path.insert(0, '.')
import asyncio, json
from app.ai.service import AIService
from app.ai.ollama_client import OllamaClient
from app.config import get_settings
from app.schemas import Email

async def test():
    s = get_settings()
    c = OllamaClient(s.ollama_base_url)
    a = AIService(c, s.ollama_model)
    with open('benchmarks/golden_emails.json') as f:
        corpus = json.load(f)
    
    for e in corpus:
        if e['id'] in ['email_explicit_other_recipient', 'email_travel_schedule']:
            email = Email(id=e['id'], subject=e['subject'], sender=e['sender'], body=e['body'], received_at='2026-08-16T10:00:00Z')
            res, _ = await a.analyze_email(email)
            print(f"{e['id']}: {[item.description for item in res.action_items]}")

asyncio.run(test())
