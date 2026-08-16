import asyncio
import json
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.schemas import Email
from app.ai.service import AIService
from app.services.task_derivation import derive_tasks
from app.config import get_settings

settings = get_settings()

async def evaluate_quality():
    corpus_path = Path(__file__).parent / "golden_emails.json"
    with open(corpus_path, "r") as f:
        corpus = json.load(f)

    from app.ai.ollama_client import OllamaClient
    client = OllamaClient(settings.ollama_base_url)
    ai_service = AIService(client, settings.ollama_model)
    
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    
    print(f"Evaluating {len(corpus)} emails with {settings.ollama_model}...")
    
    for item in corpus:
        email = Email(
            id=item["id"],
            subject=item["subject"],
            sender=item["sender"],
            body=item["body"],
            received_at="2026-08-16T10:00:00Z"
        )
        
        try:
            analysis, _ = await ai_service.analyze_email(email)
            tasks = derive_tasks(email, analysis)
            
            expected = item["expected_tasks"]
            actual = len(tasks)
            
            if actual > 0 and expected > 0:
                # We assume if it found tasks and we expected tasks, it's a TP.
                # If it found more than expected, the extra are FP.
                true_positives += min(actual, expected)
                if actual > expected:
                    false_positives += (actual - expected)
                if expected > actual:
                    false_negatives += (expected - actual)
            elif actual > 0 and expected == 0:
                false_positives += actual
                print(f"  [FP] {item['id']}: expected 0, got {actual}")
            elif actual == 0 and expected > 0:
                false_negatives += expected
                print(f"  [FN] {item['id']}: expected {expected}, got 0")
            else:
                pass # TN
                
        except Exception as e:
            print(f"Error analyzing {item['id']}: {e}")
            
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    
    print("\n--- Quality Results ---")
    print(f"True Positives: {true_positives}")
    print(f"False Positives: {false_positives}")
    print(f"False Negatives: {false_negatives}")
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")

if __name__ == "__main__":
    asyncio.run(evaluate_quality())
