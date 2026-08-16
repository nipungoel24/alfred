import pytest
from datetime import datetime, timezone
import json
import sqlite3
import tempfile
import os
from pathlib import Path

from backend.app.db.repositories import Repository
from backend.app.services.task_migration import TaskMigrationService
from backend.app.schemas import Email, EmailAnalysis, Task, ActionItem, Deadline, Priority, Category, EmailAccount

@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".sqlite3")
    os.close(fd)
    yield Path(path)
    if os.path.exists(path):
        os.remove(path)

@pytest.fixture
def repo(temp_db):
    r = Repository(temp_db)
    # The database schema will be auto-migrated by Repository/connect
    yield r
    r.close()

def test_migration_idempotency_and_preservation(repo):
    # Setup baseline data
    email_id = "test_email_1"
    account_id = "test_acc"
    thread_id = "test_thread"
    
    repo.save_account(EmailAccount(id=account_id, provider="gmail", email_address="test@test.com", display_name="Test", connection_status="connected"))
    
    email = Email(
        id=email_id,
        account_id=account_id,
        thread_id=thread_id,
        sender="boss@corp.com",
        subject="Important project",
        body="Please review the document by tomorrow.",
        received_at=datetime.now(timezone.utc),
        snippet="Please review..."
    )
    repo.upsert_email_commit(email, "fp_email_1")
    
    analysis = EmailAnalysis(
        priority="high",
        category="work",
        needs_reply=True,
        summary="Boss wants review",
        action_items=[ActionItem(description="Review the document", owner="user", deadline="tomorrow")],
        deadlines=[Deadline(description="Document review", due_at="tomorrow", confidence="explicit")],
        short_summary="Boss wants review",
        priority_score=95,
        reason_for_priority="Boss request"
    )
    repo.save_analysis(email_id, "fp_email_1", "qwen3:4b", analysis)
    
    # Pre-insert some manual state
    # 1. A pending obsolete task
    repo.con.execute("INSERT INTO tasks (id, source_email_id, title, status, fingerprint) VALUES ('old_pending', ?, 'Pending noise', 'pending', 'fp_old_pending')", (email_id,))
    # 2. A completed obsolete task
    repo.con.execute("INSERT INTO tasks (id, source_email_id, title, status, fingerprint) VALUES ('old_completed', ?, 'Completed noise', 'completed', 'fp_old_completed')", (email_id,))
    repo.con.commit()
    
    svc = TaskMigrationService(repo)
    
    # 1. First Migration
    tb1, ta1 = svc.run_migration("qwen3:4b")
    assert ta1 > 0 # Should have the newly derived task and the preserved completed task
    
    # Verify duplicate fingerprints remain zero
    duplicates = repo.con.execute("SELECT fingerprint, count(*) FROM tasks GROUP BY fingerprint HAVING count(*) > 1").fetchall()
    assert len(duplicates) == 0
    
    # Verify user state preservation
    old_pending = repo.con.execute("SELECT * FROM tasks WHERE id='old_pending'").fetchone()
    assert old_pending is None # Removed
    
    old_completed = repo.con.execute("SELECT * FROM tasks WHERE id='old_completed'").fetchone()
    assert old_completed is not None # Preserved
    assert old_completed['status'] == 'completed'
    
    # Verify source data preservation
    assert repo.email_count() == 1
    assert len(repo.accounts()) == 1
    
    # 2. Idempotent second migration
    tb2, ta2 = svc.run_migration("qwen3:4b")
    assert ta2 == ta1 # No changes
    
def test_migration_rollback(repo):
    email = Email(
        id="test_email_2", account_id="acc", thread_id="t2", sender="x@y.com",
        subject="sub", body="body", snippet="snip", received_at=datetime.now(timezone.utc)
    )
    repo.upsert_email_commit(email, "fp_email_2")
    analysis = EmailAnalysis(
        priority="high", category="work", needs_reply=False, summary="", action_items=[], deadlines=[],
        short_summary="short", priority_score=10, reason_for_priority="reason"
    )
    repo.save_analysis("test_email_2", "fp_email_2", "qwen3:4b", analysis)
    
    svc = TaskMigrationService(repo)
    initial_tasks = len(repo.tasks())
    
    # Force failure
    original = svc.repo.all_analyses_with_emails
    def crashing_analyses(model):
        yield from original(model)
        raise RuntimeError("Simulated DB error")
    
    svc.repo.all_analyses_with_emails = crashing_analyses
    
    with pytest.raises(RuntimeError):
        svc.run_migration("qwen3:4b")
        
    assert len(repo.tasks()) == initial_tasks
