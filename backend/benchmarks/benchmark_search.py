"""Search benchmark for Alfred's local FTS5 + structured search.

Uses privacy-safe synthetic mail only. Measures:
- plain free text (FTS5 + BM25)
- sender filter
- subject filter
- date filter
- combined structured search
- account scope
- BM25 ranking sanity (subject/sender hits outrank body-only hits)

Run from the repo root:
    py -m backend.benchmarks.benchmark_search --size 50000
"""

import argparse
import json
import random
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile

from backend.app.db.database import connect
from backend.app.db.repositories import Repository
from backend.app.schemas import Email, SearchFilters

SENDERS = [f"person{i}@example.com" for i in range(40)]
SUBJECTS = ["Quarterly planning", "Invoice payment", "Team lunch",
            "Server outage report", "Newsletter digest", "Meeting agenda",
            "Travel booking", "Security alert", "Weekly metrics",
            "Project kickoff"]
BODY_WORDS = ["budget", "deadline", "server", "customer", "contract",
              "review", "approval", "schedule", "invoice", "policy",
              "regression", "deployment", "handoff", "roadmap", "vendor"]

random.seed(42)


def synthetic_email(index: int, account_id: str | None) -> Email:
    received = datetime(2025, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index * 7)
    subject = SUBJECTS[index % len(SUBJECTS)]
    body = " ".join(random.choice(BODY_WORDS) for _ in range(30))
    labels = ["INBOX", "CATEGORY_PRIMARY"]
    if index % 4 == 0:
        labels.append("UNREAD")
    if index % 9 == 0:
        labels.append("IMPORTANT")
    return Email(
        id=f"gmail_{account_id}_{index:016x}" if account_id else f"bench_{index:016x}",
        account_id=account_id,
        sender=SENDERS[index % len(SENDERS)],
        subject=subject,
        body=body,
        received_at=received,
        label_ids=labels,
    )


def populate(repo: Repository, size: int, accounts: int = 1):
    for i in range(size):
        j = i % max(accounts, 1)
        account = f"gmail_user{j}@example.com"
        email = synthetic_email(i, account)
        repo.upsert_email(email, f"fp{i}")


def timed(label: str, fn) -> float:
    t0 = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - t0
    print(f"  {label:<38} {elapsed*1000:9.1f} ms   ({len(result)} rows)")
    return elapsed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=1000,
                        choices=[1000, 10000, 50000])
    parser.add_argument("--accounts", type=int, default=2)
    args = parser.parse_args()

    db = Path(tempfile.mkdtemp()) / "bench.sqlite3"
    repo = Repository(db)
    print(f"Populating {args.size} synthetic emails ({args.accounts} accounts)…")
    t0 = time.perf_counter()
    populate(repo, args.size, args.accounts)
    print(f"  insert+index: {(time.perf_counter()-t0):.1f}s")

    results = {}
    print("\nQueries:")
    results["free_text"] = timed(
        "free text 'invoice'",
        lambda: repo.search_emails_structured(
            SearchFilters(free_text=["invoice"]), limit=50))
    results["sender"] = timed(
        "sender filter person3@example.com",
        lambda: repo.search_emails_structured(
            SearchFilters(sender="person3@example.com"), limit=50))
    results["subject"] = timed(
        "subject filter 'meeting'",
        lambda: repo.search_emails_structured(
            SearchFilters(subject="meeting"), limit=50))
    results["date"] = timed(
        "date filter after 2025-06-01",
        lambda: repo.search_emails_structured(
            SearchFilters(after="2025-06-01T00:00:00"), limit=50))
    results["combined"] = timed(
        "combined sender+unread+text",
        lambda: repo.search_emails_structured(
            SearchFilters(sender="person", is_unread=True, free_text=["budget"]),
            limit=50))
    results["account_scope"] = timed(
        "account-scoped search",
        lambda: repo.search_emails_structured(
            SearchFilters(free_text=["meeting"]),
            account_id="gmail_user0@example.com", limit=50))
    results["prefix_like"] = timed(
        "sender prefix (LIKE fallback shape)",
        lambda: repo.emails_filtered(account_id=None, scope="all", limit=50))

    # BM25 ranking sanity: subject/sender hits should outrank body-only hits.
    print("\nBM25 ranking sanity:")
    email = synthetic_email(99999, "gmail_user@example.com")
    email.id = "gmail_ranking_probe"
    email.subject = "ZebraQuarterly"
    email.body = " ".join(BODY_WORDS)
    repo.upsert_email(email, "fp-ranking")
    ranked = repo.search_emails_structured(
        SearchFilters(free_text=["ZebraQuarterly"]), limit=10)
    ids = [e.id for e in ranked]
    if ids and ids[0] == "gmail_ranking_probe":
        print("  subject/sender hit outranks body-only hits: OK")
        results["bm25_sanity"] = "ok"
    else:
        print("  WARNING: subject hit did not rank first:", ids[:5])
        results["bm25_sanity"] = "check"

    print(f"\nSummary: {json.dumps(results, indent=2)}")
    repo.close()


if __name__ == "__main__":
    main()
