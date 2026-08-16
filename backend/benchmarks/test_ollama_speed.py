import asyncio
import time
import json
from pathlib import Path
from app.ai.service import AIService
from app.ai.ollama_client import OllamaClient
from app.config import get_settings
from app.schemas import Email

settings = get_settings()

async def run():
    print("Testing Ollama Speed...")
    client = OllamaClient(settings.ollama_base_url)
    ai_service = AIService(client, settings.ollama_model)
    
    corpus_path = Path(__file__).parent / "golden_emails.json"
    with open(corpus_path, "r") as f:
        corpus = json.load(f)
        
    latencies = []
    
    # Warm up
    email = Email(
        id=corpus[0]["id"], subject=corpus[0]["subject"], sender=corpus[0]["sender"],
        body=corpus[0]["body"], received_at="2026-08-16T10:00:00Z"
    )
    print("Running warmup...")
    await ai_service.analyze_email(email)
    
    # Test concurrency of 40 requests! Actually, evaluate_quality.py ran them sequentially. Let's run concurrently if possible, or sequentially to measure pure latency.
    print(f"Running {len(corpus)} emails sequentially...")
    
    for item in corpus:
        email = Email(
            id=item["id"], subject=item["subject"], sender=item["sender"],
            body=item["body"], received_at="2026-08-16T10:00:00Z"
        )
        t0 = time.perf_counter()
        await ai_service.analyze_email(email)
        t1 = time.perf_counter()
        
        latencies.append(t1 - t0)
        print(f"{item['id']} took {t1 - t0:.2f} seconds")
        
    latencies.sort()
    
    p50 = latencies[len(latencies)//2]
    p95 = latencies[int(len(latencies) * 0.95)]
    
    print("\n--- OLLAMA SPEED RESULTS ---")
    print(f"Total: {len(corpus)}")
    print(f"P50: {p50:.2f}s")
    print(f"P95: {p95:.2f}s")
    print(f"Max: {latencies[-1]:.2f}s")

if __name__ == "__main__":
    asyncio.run(run())
