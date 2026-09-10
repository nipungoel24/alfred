"""User corrections to derived tasks: durable dismissal + priority edits.

- "Not a task" hides the task and suppresses re-derivation (rebuild,
  restart) without touching the source email or its cached analysis.
- Priority edits persist, validate, and survive derivation/migration.
"""
import pytest
from fastapi.testclient import TestClient

from backend.app.schemas import Email, EmailAnalysis, Priority, Category
from backend.app.db.repositories import Repository
from backend.app.services.task_derivation import rebuild_tasks_from_analyses


@pytest.fixture
def isolated_app(tmp_path, monkeypatch):
    monkeypatch.setenv("ALFRED_RUNTIME_TOKEN", "test-secret-token-123")
    monkeypatch.setenv("ALFRED_DATABASE_PATH", str(tmp_path / "corrections.db"))
    import importlib
    from backend.app import config as config_mod
    from backend.app import main as main_mod
    importlib.reload(config_mod)
    importlib.reload(main_mod)
    yield main_mod.app, main_mod
    monkeypatch.delenv("ALFRED_RUNTIME_TOKEN")
    monkeypatch.delenv("ALFRED_DATABASE_PATH")
    importlib.reload(config_mod)
    importlib.reload(main_mod)


def _seed_derived(main_mod):
    """One analyzed email with one derived task; returns (email, task)."""
    email = Email(
        id="e1", account_id="acct_a", sender="boss@work.com",
        subject="Q3 planning needed", body="Please send the Q3 plan by Friday.",
        label_ids=["INBOX"],
    )
    main_mod.repo.upsert_email_commit(email, "fp1")
    analysis = EmailAnalysis(
        short_summary="Plan request", category=Category.work,
        priority=Priority.high, priority_score=78,
        reason_for_priority="Direct request", needs_reply=True,
        action_items=[{"description": "Send the Q3 plan", "owner": "user",
                       "deadline": "Friday"}],
        deadlines=[],
    )
    main_mod.repo.save_analysis("e1", "fp1", "test-model", analysis)
    main_mod._derive_and_save_tasks(email, analysis)
    tasks = main_mod.repo.tasks_by_email("e1")
    assert len(tasks) == 1
    return email, tasks[0]


def test_dismiss_hides_and_suppresses_rederivation(isolated_app):
    app, main_mod = isolated_app
    client = TestClient(app)
    headers = {"X-Alfred-Token": "test-secret-token-123"}
    _, task = _seed_derived(main_mod)

    r = client.post(f"/api/tasks/{task.id}/dismiss", headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "dismissed"

    # Hidden from the default projections…
    assert main_mod.repo.tasks() == []
    assert main_mod.repo.active_tasks() == []
    assert client.get("/api/tasks", headers=headers).json() == []
    # …but the row (fingerprint tombstone) survives.
    assert main_mod.repo.task(task.id).status == "dismissed"

    # Rebuild and restart must NOT resurrect it.
    added = rebuild_tasks_from_analyses(main_mod.repo, "test-model")
    assert added == 0
    assert main_mod.repo.tasks() == []

    # Source email and cached analysis are intact (only the task was rejected).
    assert main_mod.repo.email("e1") is not None
    assert main_mod.repo.cached_analysis("e1", "fp1", "test-model") is not None


def test_dismiss_unknown_task_404(isolated_app):
    app, _ = isolated_app
    client = TestClient(app)
    r = client.post("/api/tasks/nope/dismiss",
                    headers={"X-Alfred-Token": "test-secret-token-123"})
    assert r.status_code == 404


def test_dismissal_survives_reopen(tmp_path):
    from backend.app.schemas import Task
    db = tmp_path / "reopen.db"
    repo = Repository(db)
    repo.save_task(Task(id="t1", source_email_id=None, title="Do it",
                        status="pending"))
    repo.dismiss_task("t1")
    repo.close()

    repo2 = Repository(db)
    try:
        assert repo2.tasks() == []
        assert repo2.task("t1").status == "dismissed"
        assert repo2.tasks(status="dismissed")[0].id == "t1"
    finally:
        repo2.close()


def test_priority_patch_persists(isolated_app):
    app, main_mod = isolated_app
    client = TestClient(app)
    headers = {"X-Alfred-Token": "test-secret-token-123"}
    _, task = _seed_derived(main_mod)
    assert task.priority == "high"

    r = client.patch(f"/api/tasks/{task.id}", headers=headers,
                     json={"priority": "low"})
    assert r.status_code == 200
    assert r.json()["priority"] == "low"
    assert r.json()["priority_override"] == "low"

    # Visible through the API and durable across reopen.
    assert client.get("/api/tasks", headers=headers).json()[0]["priority"] == "low"


def test_priority_patch_rejects_invalid(isolated_app):
    app, main_mod = isolated_app
    client = TestClient(app)
    headers = {"X-Alfred-Token": "test-secret-token-123"}
    _, task = _seed_derived(main_mod)

    r = client.patch(f"/api/tasks/{task.id}", headers=headers,
                     json={"priority": "critical"})
    assert r.status_code == 422
    # Original priority untouched.
    assert main_mod.repo.task(task.id).priority == "high"


def test_priority_patch_unknown_task_404(isolated_app):
    app, _ = isolated_app
    client = TestClient(app)
    r = client.patch("/api/tasks/nope",
                     headers={"X-Alfred-Token": "test-secret-token-123"},
                     json={"priority": "low"})
    assert r.status_code == 404


def test_derivation_never_overwrites_user_priority(isolated_app):
    app, main_mod = isolated_app
    _, task = _seed_derived(main_mod)
    main_mod.repo.set_task_priority(task.id, "low")

    # Re-derivation (cached path) and rebuild both keep the user's choice.
    email = main_mod.repo.email("e1")
    analysis = main_mod.repo.cached_analysis("e1", "fp1", "test-model")
    main_mod._derive_and_save_tasks(email, analysis)
    assert main_mod.repo.task(task.id).priority == "low"

    rebuild_tasks_from_analyses(main_mod.repo, "test-model")
    kept = main_mod.repo.task(task.id)
    assert kept.priority == "low"
    assert kept.priority_override == "low"


def test_migration_service_respects_override(tmp_path):
    from backend.app.services.task_derivation import derive_tasks
    from backend.app.services.task_migration import TaskMigrationService

    db = tmp_path / "mig.db"
    repo = Repository(db)
    email = Email(id="e1", sender="boss@work.com",
                  subject="Q3 planning needed",
                  body="Please send the Q3 plan by Friday.",
                  label_ids=["INBOX"])
    repo.upsert_email_commit(email, "fp")
    analysis = EmailAnalysis(
        short_summary="s", category=Category.work, priority=Priority.high,
        priority_score=78, reason_for_priority="r", needs_reply=True,
        action_items=[{"description": "Send the Q3 plan", "owner": "user",
                       "deadline": "Friday"}],
        deadlines=[],
    )
    repo.save_analysis("e1", "fp", "test-model", analysis)
    # Derive once, then the user overrides the priority.
    for t in derive_tasks(email, analysis):
        repo.save_task(t)
    task = repo.tasks_by_email("e1")[0]
    repo.set_task_priority(task.id, "low")
    repo.close()

    repo2 = Repository(db)
    try:
        TaskMigrationService(repo2).run_migration("test-model")
        kept = repo2.tasks_by_email("e1")
        assert len(kept) == 1
        assert kept[0].priority == "low"
        assert kept[0].priority_override == "low"
    finally:
        repo2.close()


def test_migration_service_never_revives_dismissed(tmp_path):
    """derive -> dismiss -> TaskMigrationService -> no active task reappears,
    the tombstone remains, and the fingerprint still suppresses derivation."""
    from backend.app.services.task_derivation import derive_tasks
    from backend.app.services.task_migration import TaskMigrationService

    db = tmp_path / "tombstone.db"
    repo = Repository(db)
    email = Email(id="e1", sender="boss@work.com",
                  subject="Q3 planning needed",
                  body="Please send the Q3 plan by Friday.",
                  label_ids=["INBOX"])
    repo.upsert_email_commit(email, "fp")
    analysis = EmailAnalysis(
        short_summary="s", category=Category.work, priority=Priority.high,
        priority_score=78, reason_for_priority="r", needs_reply=True,
        action_items=[{"description": "Send the Q3 plan", "owner": "user",
                       "deadline": "Friday"}],
        deadlines=[],
    )
    repo.save_analysis("e1", "fp", "test-model", analysis)
    for t in derive_tasks(email, analysis):
        repo.save_task(t)
    task = repo.tasks_by_email("e1")[0]
    fingerprint = task.fingerprint
    assert fingerprint

    repo.dismiss_task(task.id)
    assert repo.tasks() == []
    repo.close()

    repo2 = Repository(db)
    try:
        TaskMigrationService(repo2).run_migration("test-model")
        # No active task reappears…
        assert repo2.tasks() == []
        assert repo2.active_tasks() == []
        # …the dismissed tombstone remains…
        tombstone = repo2.task(task.id)
        assert tombstone is not None
        assert tombstone.status == "dismissed"
        assert tombstone.fingerprint == fingerprint
        # …and the same fingerprint still suppresses future derivation
        # (the exact check _derive_and_save_tasks performs).
        assert repo2.task_exists_by_fingerprint(fingerprint)
        email2 = repo2.email("e1")
        analysis2 = repo2.cached_analysis("e1", "fp", "test-model")
        from backend.app.services.task_derivation import (
            derive_tasks as _derive_tasks,
            candidate_fingerprints as _candidates,
            _normalize_action as _normalize,
        )
        newcomers = [
            t for t in _derive_tasks(email2, analysis2)
            if not any(repo2.task_exists_by_fingerprint(c)
                       for c in _candidates(email2.thread_id, email2.account_id,
                                            _normalize(t.title or "")) if c)
        ]
        assert newcomers == []
    finally:
        repo2.close()
