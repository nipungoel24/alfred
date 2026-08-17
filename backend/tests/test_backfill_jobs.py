"""Durable backfill job system tests.

Covers the backend-owned orchestration: typed backfill state, persistent
job rows, not_before rate limiting, backoff/retry, priority ordering
(backfill always below analysis), and cursor resume semantics.
"""
import json
from datetime import datetime, timezone, timedelta

import pytest

from backend.app.db.repositories import Repository
from backend.app.mail.backfill import normalize_cursor, status_payload, set_state
from backend.app.mail.eligibility import BackfillState


@pytest.fixture
def repo(tmp_path):
    r = Repository(tmp_path / "backfill_jobs.db")
    yield r
    r.con.close()


def _future(seconds: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat()


def _past(seconds: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds)).isoformat()


# ═══════════════════════════════════════════════════════════════════
# TYPED STATE + CURSOR
# ═══════════════════════════════════════════════════════════════════

def test_normalize_legacy_complete_cursor():
    data = normalize_cursor(json.dumps({"backfill_complete": True, "history_id": "1"}))
    assert data["backfill_state"] == BackfillState.COMPLETE.value


def test_normalize_legacy_running_cursor():
    data = normalize_cursor(json.dumps({"backfill_page_token": "tok", "history_id": "1"}))
    assert data["backfill_state"] == BackfillState.RUNNING.value
    assert data["backfill_page_token"] == "tok"


def test_normalize_fresh_cursor():
    data = normalize_cursor(None)
    assert data["backfill_state"] == BackfillState.NOT_STARTED.value
    assert data["backfill_imported"] == 0
    assert data["backfill_pages"] == 0


def test_status_payload_remaining_estimate():
    data = normalize_cursor(None)
    data["backfill_estimate"] = 2100
    data["backfill_imported"] = 450
    data["backfill_state"] = BackfillState.RUNNING.value
    status = status_payload(data)
    assert status["state"] == "running"
    assert status["complete"] is False
    assert status["remaining_estimate"] == 1650
    assert status["imported"] == 450


def test_status_payload_complete():
    data = normalize_cursor(None)
    set_state(data, BackfillState.COMPLETE)
    status = status_payload(data)
    assert status["complete"] is True
    assert status["state"] == "complete"


# ═══════════════════════════════════════════════════════════════════
# DURABLE JOB ROW
# ═══════════════════════════════════════════════════════════════════

def test_backfill_job_is_single_durable_row(repo):
    repo.enqueue_job("backfill_gmail_a", "backfill_gmail", "gmail_a", priority=5)
    repo.enqueue_job("backfill_gmail_a", "backfill_gmail", "gmail_a", priority=5)
    assert repo.pending_job_count("backfill_gmail") == 1


def test_next_job_honours_not_before(repo):
    repo.enqueue_job("b1", "backfill_gmail", "a", priority=5, not_before=_future(60))
    assert repo.next_job("backfill_gmail") is None
    assert repo.next_job("backfill_gmail", now_iso=_future(120)) is not None


def test_requeue_resets_attempts_and_errors(repo):
    repo.enqueue_job("b1", "backfill_gmail", "a", priority=5)
    repo.update_job_status("b1", "running")
    repo.update_job_status("b1", "retryable_failed", error_code="HTTP_429", error_message="slow down")
    next_run = _future(3)
    repo.requeue_job("b1", not_before=next_run)
    job = repo.job("b1")
    assert job["status"] == "queued"
    assert job["attempts"] == 0
    assert job["error_code"] is None
    assert job["not_before"] == next_run


def test_backoff_and_promotion_cycle(repo):
    repo.enqueue_job("b1", "backfill_gmail", "a", priority=5)
    repo.update_job_status("b1", "running")
    repo.retry_job_with_backoff("b1", "HTTP_500", "boom", not_before=_future(30))
    assert repo.next_job("backfill_gmail") is None  # still backing off
    # after the backoff window elapses, promote_due_jobs re-arms it
    repo.promote_due_jobs(now_iso=_future(60))
    assert repo.next_job("backfill_gmail") is not None


def test_rearm_terminal_job_for_resume(repo):
    # A completed job row must be re-armable when the account's backfill
    # state says work remains (the INSERT OR IGNORE alone would not do it).
    repo.enqueue_job("backfill_gmail_a", "backfill_gmail", "gmail_a", priority=5)
    repo.update_job_status("backfill_gmail_a", "running")
    repo.update_job_status("backfill_gmail_a", "succeeded")
    repo.rearm_terminal_job("backfill_gmail_a")
    job = repo.job("backfill_gmail_a")
    assert job["status"] == "queued"
    assert job["attempts"] == 0
    assert job["not_before"] is None


def test_rearm_does_not_touch_backoff_retries(repo):
    repo.enqueue_job("b1", "backfill_gmail", "a", priority=5)
    repo.update_job_status("b1", "running")
    not_before = _future(120)
    repo.retry_job_with_backoff("b1", "HTTP_500", "boom", not_before=not_before)
    repo.rearm_terminal_job("b1")
    job = repo.job("b1")
    assert job["status"] == "retryable_failed"
    assert job["not_before"] == not_before


def test_backfill_priority_is_below_analysis(repo):
    repo.enqueue_job("backfill_1", "backfill_gmail", "a", priority=5)
    repo.enqueue_job("analyze_1", "analyze_email", "m1", priority=100)
    next_up = repo.next_job()  # any type, highest priority first
    assert next_up["job_type"] == "analyze_email"
    # and within the backfill type only, the backfill job is picked
    assert repo.next_job("backfill_gmail")["id"] == "backfill_1"
