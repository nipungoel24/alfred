import asyncio
import time
import json
import sqlite3
import statistics
from pathlib import Path
import os
import sys
import psutil

# Ensure we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas import Email
from app.ai.ollama_client import OllamaClient
from app.config import get_settings

settings = get_settings()

def timer(label, fn, iterations=1):
    times = []
    result = None
    for _ in range(iterations):
        start = time.perf_counter()
        if asyncio.iscoroutinefunction(fn):
            result = asyncio.run(fn())
        else:
            result = fn()
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
    
    if len(times) == 0:
        return {"label": label, "iterations": 0}
        
    return {
        "label": label,
        "p50_ms": round(statistics.median(times), 2),
        "p95_ms": round(sorted(times)[int(len(times) * 0.95)] if len(times) >= 20 else max(times), 2),
        "max_ms": round(max(times), 2),
        "min_ms": round(min(times), 2),
        "iterations": iterations,
    }

async def timer_async(label, fn, iterations=1):
    times = []
    result = None
    for _ in range(iterations):
        start = time.perf_counter()
        result = await fn()
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        
    if len(times) == 0:
        return {"label": label, "iterations": 0}
        
    return {
        "label": label,
        "p50_ms": round(statistics.median(times), 2),
        "p95_ms": round(sorted(times)[int(len(times) * 0.95)] if len(times) >= 20 else max(times), 2),
        "max_ms": round(max(times), 2),
        "min_ms": round(min(times), 2),
        "iterations": iterations,
    }

async def benchmark_ollama():
    results = []
    client = OllamaClient(settings.ollama_base_url)
    
    # 1. Cold start
    # We can't guarantee it's strictly cold unless we restart Ollama, but we'll run it once.
    print("  Benchmarking Ollama (first inference)...")
    try:
        start = time.perf_counter()
        res, metrics = await client.generate(settings.ollama_model, "Hi", None)
        cold_time = (time.perf_counter() - start) * 1000
        results.append({
            "label": "ollama_first_inference", 
            "total_ms": cold_time, 
            "metrics": {
                "total_ms": metrics.total_ms, 
                "load_ms": metrics.load_ms,
                "prompt_eval_ms": metrics.prompt_eval_ms, 
                "eval_ms": metrics.eval_ms,
                "prompt_tokens": metrics.prompt_tokens,
                "output_tokens": metrics.output_tokens,
            }
        })
        
        # 2. Warm inference
        print("  Benchmarking Ollama (warm inferences)...")
        warm_metrics_list = []
        for _ in range(5):
            start = time.perf_counter()
            _, metrics = await client.generate(settings.ollama_model, "Write a short summary", None)
            warm_metrics_list.append(metrics)
            
        results.append({
            "label": "ollama_warm_inference", 
            "p50_total_ms": round(statistics.median([m.total_ms for m in warm_metrics_list]), 2),
            "p50_load_ms": round(statistics.median([m.load_ms for m in warm_metrics_list]), 2),
            "p50_prompt_eval_ms": round(statistics.median([m.prompt_eval_ms for m in warm_metrics_list]), 2),
            "p50_eval_ms": round(statistics.median([m.eval_ms for m in warm_metrics_list]), 2),
            "p50_prompt_tokens": round(statistics.median([m.prompt_tokens for m in warm_metrics_list]), 2),
            "p50_output_tokens": round(statistics.median([m.output_tokens for m in warm_metrics_list]), 2),
            "iterations": 5
        })
    except Exception as e:
        print(f"Ollama benchmark failed: {e}")
        
    return results

def benchmark_db(db_path: Path):
    results = []
    if not db_path.exists():
        return results
    
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    
    email_count = con.execute("SELECT COUNT(*) FROM emails").fetchone()[0]
    
    if email_count > 0:
        # Load 50
        r = timer("db_inbox_query_50", lambda: con.execute("SELECT * FROM emails LIMIT 50").fetchall(), 10)
        results.append(r)
        
        if email_count >= 500:
            r = timer("db_inbox_query_500", lambda: con.execute("SELECT * FROM emails LIMIT 500").fetchall(), 5)
            results.append(r)
            
        # Search
        r = timer("db_search_like", lambda: con.execute("SELECT id FROM emails WHERE subject_col LIKE '%test%' OR sender_col LIKE '%test%' LIMIT 50").fetchall(), 5)
        results.append(r)
        
        # Check plan
        plan = con.execute("EXPLAIN QUERY PLAN SELECT id FROM emails WHERE subject_col LIKE '%test%' OR sender_col LIKE '%test%' LIMIT 50").fetchall()
        results.append({"label": "explain_plan_search", "plan": [dict(p) for p in plan]})
        
    # Check WAL
    wal_mode = con.execute("PRAGMA journal_mode").fetchone()[0]
    results.append({"label": "db_journal_mode", "mode": wal_mode})
    
    return results

def measure_resources():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return {
        "rss_mb": round(mem_info.rss / 1024 / 1024, 2),
        "vms_mb": round(mem_info.vms / 1024 / 1024, 2)
    }

async def main():
    print("Running comprehensive benchmarks...")
    
    results = {}
    
    # 1. Resource usage
    results["resources"] = measure_resources()
    
    # 2. Database
    db_path = Path(__file__).parent.parent / "persistent.db"
    results["database"] = benchmark_db(db_path)
    
    # 3. Ollama
    results["ollama"] = await benchmark_ollama()
    
    # Write to file
    out_file = Path(__file__).parent / "baseline_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Benchmark complete. Results saved to {out_file}")

if __name__ == "__main__":
    asyncio.run(main())
