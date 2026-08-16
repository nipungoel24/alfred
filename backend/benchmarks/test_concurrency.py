import asyncio
import time
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.ai.service import AIService
from app.config import get_settings
from app.ai.ollama_client import OllamaClient
from app.schemas import Email

settings = get_settings()

async def run_concurrent(client, count, concurrency):
    sem = asyncio.Semaphore(concurrency)
    ai = AIService(client, settings.ollama_model)
    
    email = Email(
        id="concurrency_test",
        subject="Test",
        sender="test@test.com",
        body="This is a test email body for concurrency testing.",
        received_at="2026-08-16T10:00:00Z"
    )

    async def worker(i):
        async with sem:
            start = time.perf_counter()
            await ai.analyze_email(email)
            return time.perf_counter() - start

    start_total = time.perf_counter()
    tasks = [worker(i) for i in range(count)]
    results = await asyncio.gather(*tasks)
    total_time = time.perf_counter() - start_total
    
    return total_time, results

async def main():
    client = OllamaClient(settings.ollama_base_url)
    
    # Warm up
    await client.generate(settings.ollama_model, "Hi", None)
    
    print("Testing Concurrency 1 (4 requests)...")
    c1_total, c1_res = await run_concurrent(client, 4, 1)
    print(f"  Total: {c1_total:.2f}s, per request: {[round(r, 2) for r in c1_res]}s")
    
    print("Testing Concurrency 2 (4 requests)...")
    c2_total, c2_res = await run_concurrent(client, 4, 2)
    print(f"  Total: {c2_total:.2f}s, per request: {[round(r, 2) for r in c2_res]}s")

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    asyncio.run(main())
