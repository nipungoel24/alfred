import sys; sys.path.insert(0, '.')
import asyncio
from app.ai.service import AIService
from app.ai.ollama_client import OllamaClient
from app.config import get_settings
from app.schemas import Email
from app.services.task_derivation import derive_tasks

cases = {
    "A": "Please verify the account details and send me confirmation.",
    "B": "Your account verification was completed successfully.",
    "C": "Please contact support before Friday and let me know the outcome.",
    "D": "Contact support if you need any help."
}

async def test():
    s = get_settings()
    c = OllamaClient(s.ollama_base_url)
    a = AIService(c, s.ollama_model)
    
    for k, v in cases.items():
        email = Email(id=k, subject="Test", sender="test@test.com", body=v, received_at="2026-08-16T10:00:00Z")
        analysis, _ = await a.analyze_email(email)
        tasks = derive_tasks(email, analysis)
        print(f"{k} actual: {'USER TASK' if len(tasks) > 0 else 'NO TASK'}")

asyncio.run(test())
