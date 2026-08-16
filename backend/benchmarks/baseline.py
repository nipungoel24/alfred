"""
Alfred Performance Benchmark Harness

Captures baseline metrics before engineering hardening.
Run from repository root: py -m backend.benchmarks.baseline
"""
import time
import json
import sqlite3
import statistics
from pathlib import Path
import os
import sys

# Ensure we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))


def timer(label, fn, iterations=1):
    """Run fn `iterations` times and return timing dict."""
    times = []
    result = None
    for _ in range(iterations):
        start = time.perf_counter()
        result = fn()
        elapsed = (time.perf_counter() - start) * 1000  # ms
        times.append(elapsed)
    return {
        "label": label,
        "p50_ms": round(statistics.median(times), 2) if times else 0,
        "p95_ms": round(sorted(times)[int(len(times) * 0.95)] if len(times) >= 20 else max(times), 2),
        "max_ms": round(max(times), 2),
        "min_ms": round(min(times), 2),
        "iterations": iterations,
        "result": result
    }


def benchmark_db(db_path: Path):
    """Benchmark SQLite query patterns."""
    results = []
    
    if not db_path.exists():
        print(f"  Database not found at {db_path}, skipping DB benchmarks")
        return results
    
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    
    # Count records
    email_count = con.execute("SELECT COUNT(*) FROM emails").fetchone()[0]
    analysis_count = con.execute("SELECT COUNT(*) FROM email_analysis").fetchone()[0]
    task_count = con.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    account_count = con.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
    
    results.append({"label": "record_counts", "emails": email_count, "analyses": analysis_count, "tasks": task_count, "accounts": account_count})
    
    # Benchmark: Load all emails
    r = timer("db_load_all_emails", lambda: con.execute("SELECT payload FROM emails ORDER BY imported_at DESC").fetchall(), 5)
    r["row_count"] = email_count
    results.append(r)
    
    # Benchmark: Load emails by account (if accounts exist)
    if account_count > 0:
        acc_id = con.execute("SELECT id FROM accounts LIMIT 1").fetchone()[0]
        r = timer("db_load_emails_by_account", lambda: con.execute("SELECT payload FROM emails WHERE account_id=? ORDER BY imported_at DESC", (acc_id,)).fetchall(), 5)
        results.append(r)
    
    # Benchmark: Load all tasks
    r = timer("db_load_all_tasks", lambda: con.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall(), 5)
    r["row_count"] = task_count
    results.append(r)
    
    # Benchmark: Load all analyses
    r = timer("db_load_all_analyses", lambda: con.execute("SELECT * FROM email_analysis").fetchall(), 5)
    r["row_count"] = analysis_count
    results.append(r)
    
    # Benchmark: Single email lookup
    if email_count > 0:
        sample_id = con.execute("SELECT id FROM emails LIMIT 1").fetchone()[0]
        r = timer("db_single_email_lookup", lambda: con.execute("SELECT payload FROM emails WHERE id=?", (sample_id,)).fetchall(), 10)
        results.append(r)
    
    # Benchmark: Pydantic deserialization
    if email_count > 0:
        from app.schemas import Email
        rows = con.execute("SELECT payload FROM emails LIMIT 50").fetchall()
        r = timer("pydantic_deserialize_50_emails", lambda: [Email.model_validate_json(row["payload"]) for row in rows], 3)
        results.append(r)
    
    # Benchmark: Python-level search simulation
    if email_count > 0:
        from app.schemas import Email
        def python_search():
            rows = con.execute("SELECT payload FROM emails").fetchall()
            emails = [Email.model_validate_json(row["payload"]) for row in rows]
            return [e for e in emails if "test" in (e.subject + " " + e.sender + " " + e.body).lower()]
        r = timer("python_search_all_emails", python_search, 3)
        results.append(r)
    
    # Benchmark: EXPLAIN QUERY PLAN for common queries
    plans = []
    for query_name, query in [
        ("all_emails_ordered", "SELECT payload FROM emails ORDER BY imported_at DESC"),
        ("emails_by_account", "SELECT payload FROM emails WHERE account_id='test' ORDER BY imported_at DESC"),
        ("emails_by_thread", "SELECT payload FROM emails WHERE thread_id='test'"),
        ("analysis_by_email", "SELECT payload FROM email_analysis WHERE email_id='test' AND content_hash='test' AND model_name='test' AND schema_version='1'"),
        ("tasks_ordered", "SELECT * FROM tasks ORDER BY created_at DESC"),
        ("tasks_by_source", "SELECT * FROM tasks WHERE source_email_id='test'"),
    ]:
        plan_rows = con.execute(f"EXPLAIN QUERY PLAN {query}").fetchall()
        plan_text = " | ".join([str(dict(r)) for r in plan_rows])
        plans.append({"query": query_name, "plan": plan_text})
    
    results.append({"label": "query_plans", "plans": plans})
    
    # Check current PRAGMA settings
    pragma_results = {}
    for pragma in ["journal_mode", "synchronous", "busy_timeout", "foreign_keys", "cache_size"]:
        val = con.execute(f"PRAGMA {pragma}").fetchone()
        pragma_results[pragma] = val[0] if val else None
    results.append({"label": "pragma_settings", **pragma_results})
    
    # Database file size
    results.append({"label": "db_file_size_bytes", "size": db_path.stat().st_size})
    
    con.close()
    return results


def benchmark_pydantic_overhead():
    """Measure Pydantic model overhead."""
    from app.schemas import Email, EmailAnalysis
    import json as json_mod
    
    results = []
    
    # Schema generation
    r = timer("pydantic_email_schema_gen", lambda: Email.model_json_schema(), 10)
    results.append(r)
    
    r = timer("pydantic_analysis_schema_gen", lambda: EmailAnalysis.model_json_schema(), 10)
    results.append(r)
    
    return results


def main():
    print("=" * 60)
    print("ALFRED PERFORMANCE BASELINE")
    print("=" * 60)
    
    # Determine DB path
    db_path = Path(os.getenv("ALFRED_DATABASE_PATH", Path(os.getenv("LOCALAPPDATA", ".")) / "Alfred" / "alfred.sqlite3"))
    print(f"\nDatabase path: {db_path}")
    print(f"Database exists: {db_path.exists()}")
    
    all_results = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), "db_path": str(db_path)}
    
    # DB benchmarks
    print("\n--- Database Benchmarks ---")
    db_results = benchmark_db(db_path)
    for r in db_results:
        if "p50_ms" in r:
            print(f"  {r['label']}: p50={r['p50_ms']}ms  max={r['max_ms']}ms")
        elif "label" in r:
            print(f"  {r['label']}: {json.dumps({k:v for k,v in r.items() if k != 'label'}, indent=2, default=str)[:200]}")
    all_results["database"] = db_results
    
    # Pydantic benchmarks
    print("\n--- Pydantic Benchmarks ---")
    pydantic_results = benchmark_pydantic_overhead()
    for r in pydantic_results:
        print(f"  {r['label']}: p50={r['p50_ms']}ms  max={r['max_ms']}ms")
    all_results["pydantic"] = pydantic_results
    
    # Save results
    output_dir = Path(__file__).parent
    output_path = output_dir / "baseline_results.json"
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")
    
    print("\n" + "=" * 60)
    print("BASELINE CAPTURE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
