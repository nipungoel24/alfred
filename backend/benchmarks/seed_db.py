import sqlite3
import time
import random
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import get_settings

def seed_and_search():
    db_path = get_settings().database_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
        
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA journal_mode=WAL")
    
    # We will insert in batches
    # First, let's see how many we have
    count = con.execute("SELECT COUNT(*) FROM emails").fetchone()[0]
    
    target_sizes = [5000, 25000]
    
    for target in target_sizes:
        to_insert = target - count
        if to_insert > 0:
            print(f"Inserting {to_insert} emails to reach {target}...")
            batch = []
            for i in range(to_insert):
                email_id = f"test_email_{count + i}"
                payload = '{"id":"' + email_id + '","sender":"test_sender@example.com","subject":"Subject test synthetic ' + str(i) + (' needle' if i % 1000 == 0 else '') + '","body":"This is a synthetic body."}'
                batch.append((
                    email_id,
                    payload,
                    f"hash_{i}",
                    "2026-08-16T10:00:00Z",
                    "gmail_test@example.com",
                    f"thread_{i}",
                    "test_sender@example.com",
                    f"Subject test synthetic {i} " + ("needle" if i % 1000 == 0 else ""),
                    "2026-08-16T10:00:00Z"
                ))
                
                if len(batch) >= 1000:
                    con.executemany("""
                        INSERT INTO emails (id, payload, content_hash, imported_at, account_id, thread_id, sender_col, subject_col, received_at_col)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, batch)
                    batch = []
            
            if batch:
                con.executemany("""
                        INSERT INTO emails (id, payload, content_hash, imported_at, account_id, thread_id, sender_col, subject_col, received_at_col)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, batch)
            con.commit()
            count = target
        
        print(f"Testing search at {target} size...")
        # Benchmark LIKE search
        times = []
        for _ in range(5):
            start = time.perf_counter()
            res = con.execute("SELECT id FROM emails WHERE subject_col LIKE '%needle%' OR sender_col LIKE '%needle%' LIMIT 50").fetchall()
            times.append((time.perf_counter() - start) * 1000)
            
        p50 = sorted(times)[len(times)//2]
        p95 = sorted(times)[int(len(times)*0.95)] if len(times) >= 20 else max(times)
        
        print(f"  {target} rows -> p50: {p50:.2f}ms, p95: {p95:.2f}ms")

if __name__ == "__main__":
    seed_and_search()
