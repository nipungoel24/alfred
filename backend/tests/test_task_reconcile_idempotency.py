"""Reconcile / migration contract: idempotency, duplicates, preservation.

The reconciler is the only path that changes the tasks table, so these tests
pin the properties that make it safe to run on every startup:

* running it twice changes nothing the second time
* it never inflates the task count
* it never duplicates a task
* it corrects a stale row in place rather than adding a second copy
* it preserves status, created_at and a user's priority override
* it only removes a rejected task the user never acted on
"""

import os
import shutil
import sqlite3
import tempfile
from pathlib import Path

import pytest

from backend.app.db.repositories import Repository
from backend.app.schemas import (
    ActionItem,
    Category,
    Deadline,
    Email,
    EmailAnalysis,
    Priority,
    Task,
)
from backend.app.services.task_derivation import (
    DERIVATION_VERSION,
    reconcile_tasks_from_analyses,
    rebuild_tasks_from_analyses,
)
from backend.app.services.task_migration import TaskMigrationService

MODEL = "qwen3:4b"


# ── fixtures ──────────────────────────────────────────────────────────

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
    yield r
    r.close()


def make_email(email_id: str, thread_id: str, subject="Test", labels=None) -> Email:
    return Email(
        id=email_id,
        thread_id=thread_id,
        account_id="acct-1",
        sender="someone@example.com",
        sender_name="Someone",
        recipients=["me@example.com"],
        subject=subject,
        body="Please submit the signed NDA by 12 September 2026.",
        received_at="2026-09-01T10:00:00+00:00",
        label_ids=labels if labels is not None else ["INBOX"],
    )


def make_analysis(**kw) -> EmailAnalysis:
    base = dict(
        short_summary="Test",
        category=Category.work,
        priority=Priority.high,
        priority_score=80,
        reason_for_priority="Test",
        needs_reply=True,
    )
    base.update(kw)
    return EmailAnalysis(**base)


def store(repo, email: Email, analysis: EmailAnalysis):
    """Persist an email and its analysis the way the sync path does."""
    from backend.app.mail.fingerprint import content_fingerprint
    fp = content_fingerprint(email)
    repo.upsert_email(email, fp)
    repo.save_analysis(email.id, fp, MODEL, analysis)


def seed_realistic_backlog(repo):
    """A backlog holding one good task and one of each historical defect."""
    # 1. A genuine action, plus a stale prose due date from the old logic.
    e1 = make_email("e-good", "t-good")
    store(repo, e1, make_analysis(action_items=[
        ActionItem(description="Submit the signed NDA", owner="user",
                   deadline="due_at: soon"),
    ]))
    # 2. A deadline entry whose description is a bare date: became a bad title.
    e2 = make_email("e-date", "t-date")
    store(repo, e2, make_analysis(deadlines=[
        Deadline(description="12th September 2026", due_at="2026-09-12T00:00:00+00:00",
                 confidence="explicit"),
    ]))
    # 3. "No action required" - the model meant there is no task.
    e3 = make_email("e-noaction", "t-noaction")
    store(repo, e3, make_analysis(action_items=[
        ActionItem(description="No action required"),
    ]))
    # 4. A marketing blast with a community-channel CTA.
    e4 = make_email("e-marketing", "t-marketing")
    store(repo, e4, make_analysis(category=Category.promotion, needs_reply=False,
                                  action_items=[
        ActionItem(description="Join Techugo Campus Drive WhatsApp Channel", owner="user"),
    ]))
    # 5. A real second action, so the count is not trivially 1.
    e5 = make_email("e-good2", "t-good2")
    store(repo, e5, make_analysis(action_items=[
        ActionItem(description="Reply to the recruiter", owner="user"),
    ]))
    return repo


# ── one run ───────────────────────────────────────────────────────────

def test_reconcile_corrects_stale_rows_and_removes_invalid(repo):
    seed_realistic_backlog(repo)
    report = reconcile_tasks_from_analyses(repo, MODEL)

    titles = sorted(t.title for t in repo.tasks_all())
    # The date-as-title and the "no action" and the marketing CTA are gone.
    assert titles == ["Reply to the recruiter", "Submit the signed NDA"]
    # The stale prose due date is corrected to null, not carried forward.
    good = next(t for t in repo.tasks_all() if t.title == "Submit the signed NDA")
    assert good.due_at is None
    # owner is a real field now, not a line inside description.
    assert good.owner == "user"
    assert good.description is None
    assert report.before == 0
    assert report.recreated == 2
    assert report.after == 2


def test_reconcile_normalizes_an_existing_stale_row_in_place(repo):
    seed_realistic_backlog(repo)
    reconcile_tasks_from_analyses(repo, MODEL)

    # Re-introduce the historical corruption exactly as it was stored.
    row = repo.con.execute(
        "UPDATE tasks SET due_at='due_at: soon', description='Owner: user', "
        "derivation_version='2' WHERE title='Submit the signed NDA'").rowcount
    assert row == 1
    before_id = next(t.id for t in repo.tasks_all() if t.title == "Submit the signed NDA")

    report = reconcile_tasks_from_analyses(repo, MODEL)

    after = repo.tasks_all()
    assert len(after) == 2, "must be corrected in place, not duplicated"
    fixed = next(t for t in after if t.id == before_id)
    assert fixed.due_at is None
    assert fixed.description is None
    assert fixed.derivation_version == DERIVATION_VERSION
    assert report.normalized >= 1
    assert report.recreated == 0


# ── idempotency: the mandatory property ───────────────────────────────

def test_running_the_migration_twice_changes_nothing_the_second_time(repo):
    seed_realistic_backlog(repo)

    first = reconcile_tasks_from_analyses(repo, MODEL)
    snapshot_a = sorted(
        (t.id, t.title, t.due_at, t.owner, t.priority, t.status, t.created_at,
         t.derivation_version)
        for t in repo.tasks_all()
    )
    count_a = len(snapshot_a)

    second = reconcile_tasks_from_analyses(repo, MODEL)
    snapshot_b = sorted(
        (t.id, t.title, t.due_at, t.owner, t.priority, t.status, t.created_at,
         t.derivation_version)
        for t in repo.tasks_all()
    )

    assert snapshot_b == snapshot_a, "second run must be a no-op"
    assert len(snapshot_b) == count_a, "no task count inflation"
    # Nothing created, removed, normalised or duplicated on the second pass.
    assert second.recreated == 0
    assert second.removed == 0
    assert second.duplicates == 0
    assert second.normalized == 0
    assert second.preserved == count_a
    assert second.after == first.after


def test_running_the_rebuild_twice_is_stable(repo):
    seed_realistic_backlog(repo)
    n1 = rebuild_tasks_from_analyses(repo, MODEL)
    snap1 = sorted((t.id, t.title, t.due_at) for t in repo.tasks_all())
    n2 = rebuild_tasks_from_analyses(repo, MODEL)
    snap2 = sorted((t.id, t.title, t.due_at) for t in repo.tasks_all())
    assert snap1 == snap2
    assert n2 == 0, "the second rebuild must not add anything"


def test_migration_service_is_idempotent(repo):
    seed_realistic_backlog(repo)
    before, after = TaskMigrationService(repo).run_migration(MODEL)
    assert before == 0 and after == 2
    before2, after2 = TaskMigrationService(repo).run_migration(MODEL)
    assert (before2, after2) == (2, 2)
    assert len(repo.tasks_all()) == 2


# ── preservation ──────────────────────────────────────────────────────

def test_user_state_is_preserved_across_a_reconcile(repo):
    seed_realistic_backlog(repo)
    reconcile_tasks_from_analyses(repo, MODEL)

    target = next(t for t in repo.tasks_all() if t.title == "Submit the signed NDA")
    # The user completes it and overrides the priority.
    repo.con.execute(
        "UPDATE tasks SET status='completed', priority='low', priority_override='low', "
        "created_at='2020-01-01T00:00:00+00:00' WHERE id=?", (target.id,))
    repo.con.commit()

    report = reconcile_tasks_from_analyses(repo, MODEL)

    kept = repo.con.execute(
        "SELECT status, priority, priority_override, created_at FROM tasks WHERE id=?",
        (target.id,)).fetchone()
    assert kept[0] == "completed"
    assert kept[1] == "low", "a user priority edit must win over the extractor"
    assert kept[2] == "low"
    assert kept[3] == "2020-01-01T00:00:00+00:00", "created_at must be preserved"
    assert report.normalized == 0


def test_a_completed_task_the_extractor_rejects_is_kept(repo):
    seed_realistic_backlog(repo)
    reconcile_tasks_from_analyses(repo, MODEL)
    # Mark the marketing task completed *before* the logic stops producing it.
    seed_rows = repo.con.execute(
        "SELECT id FROM tasks WHERE title='Reply to the recruiter'").fetchone()
    assert seed_rows

    # Now add a task the extractor will reject, and mark it completed.
    e6 = make_email("e-done", "t-done")
    store(repo, e6, make_analysis(action_items=[
        ActionItem(description="No action required"),
    ]))
    rejected = repo.con.execute(
        "SELECT id FROM tasks WHERE title='No action required'").fetchone()
    # It was never derived under the corrected logic, so insert it directly to
    # simulate a task the user had already closed before the rules changed.
    repo.con.execute(
        "INSERT INTO tasks (id, source_email_id, source_thread_id, title, description,"
        " due_at, owner, priority, status, created_at, derivation_version, confidence, fingerprint)"
        " VALUES ('legacy-done','e-done','t-done','No action required',NULL,NULL,NULL,"
        "'low','completed','2019-01-01T00:00:00+00:00','2','low','fp-legacy-done')")
    repo.con.commit()

    report = reconcile_tasks_from_analyses(repo, MODEL)

    still_there = repo.con.execute(
        "SELECT status FROM tasks WHERE id='legacy-done'").fetchone()
    assert still_there is not None, "a completed task must never be deleted"
    assert still_there[0] == "completed"
    assert report.kept_user_state >= 1


def test_pending_rejected_task_is_removed(repo):
    seed_realistic_backlog(repo)
    reconcile_tasks_from_analyses(repo, MODEL)
    repo.con.execute(
        "INSERT INTO tasks (id, source_email_id, source_thread_id, title, description,"
        " due_at, owner, priority, status, created_at, derivation_version, confidence, fingerprint)"
        " VALUES ('legacy-pending','e-noaction','t-noaction','12th September 2026',NULL,"
        "'due_at: soon',NULL,'low','pending','2019-01-01T00:00:00+00:00','2','low','fp-legacy-pending')")
    repo.con.commit()
    assert len(repo.tasks_all()) == 3

    report = reconcile_tasks_from_analyses(repo, MODEL)

    assert repo.con.execute(
        "SELECT COUNT(*) FROM tasks WHERE id='legacy-pending'").fetchone()[0] == 0
    assert report.removed == 1
    assert len(repo.tasks_all()) == 2


# ── duplicate prevention ──────────────────────────────────────────────

def test_duplicate_stored_rows_collapse_to_one(repo):
    seed_realistic_backlog(repo)
    reconcile_tasks_from_analyses(repo, MODEL)
    original = next(t for t in repo.tasks_all() if t.title == "Submit the signed NDA")

    # Simulate the duplication hazard: a later second row, same fingerprint -
    # exactly what a re-derivation that skipped existing rows would leave behind.
    repo.con.execute(
        "INSERT INTO tasks (id, source_email_id, source_thread_id, title, description,"
        " due_at, owner, priority, status, created_at, derivation_version, confidence, fingerprint)"
        " VALUES ('dup-copy',?,?,?,'Owner: user','due_at: soon',NULL,'low','pending',"
        "'2099-01-01T00:00:00+00:00','2','low',?)",
        (original.source_email_id, original.source_thread_id, original.title,
         original.fingerprint))
    repo.con.commit()
    assert len(repo.tasks_all()) == 3

    report = reconcile_tasks_from_analyses(repo, MODEL)

    remaining = repo.tasks_all()
    assert len(remaining) == 2, "the duplicate must not survive"
    assert repo.con.execute(
        "SELECT COUNT(*) FROM tasks WHERE id='dup-copy'").fetchone()[0] == 0
    assert report.duplicates == 1
    # The original row is the one kept.
    assert any(t.id == original.id for t in remaining)


def test_two_messages_with_the_same_action_do_not_collapse(repo):
    # Different threads, same wording: two real tasks, not one.
    for n in (1, 2):
        e = make_email(f"e-same-{n}", f"t-same-{n}")
        store(repo, e, make_analysis(action_items=[
            ActionItem(description="Submit the signed NDA", owner="user"),
        ]))
    reconcile_tasks_from_analyses(repo, MODEL)
    assert len(repo.tasks_all()) == 2
    reconcile_tasks_from_analyses(repo, MODEL)
    assert len(repo.tasks_all()) == 2


def test_source_linkage_survives(repo):
    seed_realistic_backlog(repo)
    reconcile_tasks_from_analyses(repo, MODEL)
    for t in repo.tasks_all():
        assert t.source_email_id, "every derived task keeps its source email"
        assert t.source_thread_id, "every derived task keeps its source thread"
    report = reconcile_tasks_from_analyses(repo, MODEL)
    assert report.linked == 2
    assert report.unlinked == 0


# ── a real copy of the live database ──────────────────────────────────

def _live_db() -> Path | None:
    p = Path(os.environ.get("LOCALAPPDATA", "")) / "Alfred" / "alfred.sqlite3"
    return p if p.exists() else None


@pytest.mark.skipif(_live_db() is None, reason="no live mailbox database present")
def test_reconcile_on_a_copy_of_the_live_database_is_idempotent(tmp_path):
    """The real 291-row backlog, on a copy. The live file is never opened."""
    copy = tmp_path / "live-copy.sqlite3"
    shutil.copy2(_live_db(), copy)

    con = sqlite3.connect(str(copy))
    r = Repository(copy)
    try:
        before = r.con.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        assert before > 0

        def snapshot():
            return sorted(tuple(r) for r in r.con.execute(
                "SELECT id, title, due_at, status, derivation_version FROM tasks"))

        first = reconcile_tasks_from_analyses(r, MODEL)
        rows_a = snapshot()
        count_a = len(rows_a)

        second = reconcile_tasks_from_analyses(r, MODEL)
        rows_b = snapshot()

        assert rows_b == rows_a, "second pass on real data must be a no-op"
        assert len(rows_b) == count_a, "no inflation on real data"
        assert second.recreated == 0
        assert second.normalized == 0
        assert second.removed == 0
        assert second.duplicates == 0
        assert second.after == count_a
        # The first pass must have done the work.
        assert first.after <= first.before
    finally:
        r.close()
        con.close()
