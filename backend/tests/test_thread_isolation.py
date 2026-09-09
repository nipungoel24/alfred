"""Thread isolation: provider thread IDs are NOT globally unique.

Covers P0-1:
- canonical scoped thread identity via production normalization
- emails_by_thread account scoping (legacy raw + scoped rows)
- draft endpoint never mixes cross-account thread content into the AI prompt
- thread re-key migration for legacy databases
- task fingerprint dual-form dedupe across the thread migration
"""
import base64
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.schemas import Email
from backend.app.db.repositories import Repository
from backend.app.mail.providers.gmail import GmailProvider
from backend.app.mail.identity import (
    scoped_email_id, scoped_thread_id, parse_thread_id, strip_scope,
)
from backend.app.services.task_derivation import (
    task_fingerprint, candidate_fingerprints, _normalize_action,
)


@pytest.fixture
def isolated_app(tmp_path, monkeypatch):
    """Reload the FastAPI app against a scratch database (same pattern as
    test_desktop_auth.authed_app, local so this module is self-contained)."""
    monkeypatch.setenv("ALFRED_RUNTIME_TOKEN", "test-secret-token-123")
    monkeypatch.setenv("ALFRED_DATABASE_PATH", str(tmp_path / "threads.db"))
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

PROVIDER_THREAD = "18c4ab91ef02cd10"
RAW_A = "1a076e26cf3a3533"
RAW_B = "1a07b61f84a314c5"


def gmail_detail(raw_id: str, subject: str, sender: str):
    return {
        "id": raw_id,
        "threadId": PROVIDER_THREAD,
        "internalDate": "1754312400000",
        "labelIds": ["INBOX", "CATEGORY_PRIMARY"],
        "snippet": "",
        "payload": {
            "headers": [
                {"name": "From", "value": sender},
                {"name": "Subject", "value": subject},
                {"name": "To", "value": "me@example.com"},
            ],
            "body": {"data": base64.urlsafe_b64encode(b"body").decode()},
        },
    }


@pytest.fixture
def provider():
    return GmailProvider(client_id="test-client", client_secret="")


def test_scoped_thread_identity(provider):
    email_a = provider._normalize_message(
        gmail_detail(RAW_A, "A", "a@example.com"), "gmail_a@example.com")
    email_b = provider._normalize_message(
        gmail_detail(RAW_B, "B", "b@example.com"), "gmail_b@example.com")

    assert email_a.thread_id != email_b.thread_id
    assert email_a.thread_id == scoped_thread_id("gmail_a@example.com", PROVIDER_THREAD)
    assert parse_thread_id(email_a.thread_id) == ("gmail_a@example.com", PROVIDER_THREAD)
    # Raw provider thread id survives in source metadata for forensics.
    assert email_a.source_metadata["gmail_raw"]["threadId"] == PROVIDER_THREAD


def test_thread_query_isolation(tmp_path: Path, provider):
    repo = Repository(tmp_path / "test.sqlite3")
    email_a = provider._normalize_message(
        gmail_detail(RAW_A, "A", "a@example.com"), "gmail_a@example.com")
    email_b = provider._normalize_message(
        gmail_detail(RAW_B, "B", "b@example.com"), "gmail_b@example.com")
    repo.upsert_email_commit(email_a, "fp_a")
    repo.upsert_email_commit(email_b, "fp_b")

    only_a = repo.emails_by_thread(email_a.thread_id, account_id="gmail_a@example.com")
    assert [e.id for e in only_a] == [email_a.id]

    # Cross-account probe: B's scoped thread under A's account finds nothing.
    assert repo.emails_by_thread(email_b.thread_id, account_id="gmail_a@example.com") == []
    # Legacy defense: a raw provider thread id without account still only
    # matches rows that literally carry it (none, post-normalization).
    assert repo.emails_by_thread(PROVIDER_THREAD, account_id="gmail_a@example.com") == []


def test_draft_endpoint_isolation(isolated_app, provider):
    """The AI draft prompt for A must contain ONLY A's thread messages."""
    app, main_mod = isolated_app
    client = TestClient(app)

    email_a = provider._normalize_message(
        gmail_detail(RAW_A, "Secret plan A", "a@example.com"), "gmail_a@example.com")
    email_b = provider._normalize_message(
        gmail_detail(RAW_B, "Secret plan B", "b@example.com"), "gmail_b@example.com")
    main_mod.repo.upsert_email_commit(email_a, "fp_a")
    main_mod.repo.upsert_email_commit(email_b, "fp_b")

    captured: dict = {}

    async def fake_draft(email, thread_emails=None):
        captured["email_id"] = email.id
        captured["thread_ids"] = [e.id for e in (thread_emails or [])]
        captured["subjects"] = [e.subject for e in (thread_emails or [])]
        return "draft text"

    main_mod.ai.draft_reply = fake_draft  # type: ignore[method-assign]
    try:
        r = client.post(
            f"/api/emails/{email_a.id}/draft",
            headers={"X-Alfred-Token": "test-secret-token-123"},
        )
        assert r.status_code == 200
        assert captured["email_id"] == email_a.id
        assert captured["thread_ids"] == [email_a.id]
        assert "Secret plan B" not in captured["subjects"]

        r = client.post(
            f"/api/emails/{email_b.id}/draft",
            headers={"X-Alfred-Token": "test-secret-token-123"},
        )
        assert r.status_code == 200
        assert captured["thread_ids"] == [email_b.id]
        assert "Secret plan A" not in captured["subjects"]
    finally:
        import importlib
        importlib.reload(main_mod)


def test_thread_migration_rekeys_legacy_rows(tmp_path: Path):
    """Legacy (raw thread id) rows migrate to scoped threads with tasks."""
    import sqlite3
    from backend.app.db.database import connect, SCHEMA, INDEXES

    db = tmp_path / "legacy_threads.sqlite3"
    con = sqlite3.connect(db)
    con.executescript(SCHEMA)
    con.executescript(INDEXES)
    account_id = "gmail_nipun@example.com"
    email = Email(
        id="1a076e26cf3a3533", account_id=account_id, thread_id=PROVIDER_THREAD,
        sender="a@example.com", subject="Hi", body="body",
        source_metadata={"gmail_raw": {"labelIds": ["INBOX"], "threadId": PROVIDER_THREAD}},
    )
    con.execute(
        "INSERT INTO emails (id, payload, content_hash, imported_at, account_id, thread_id) "
        "VALUES (?,?,?,?,?,?)",
        ("1a076e26cf3a3533", email.model_dump_json(), "fp",
         "2026-01-01T00:00:00", account_id, PROVIDER_THREAD),
    )
    con.execute(
        "INSERT INTO tasks (id, source_email_id, source_thread_id, title, status) "
        "VALUES ('task-1', '1a076e26cf3a3533', ?, 'Do thing', 'pending')",
        (PROVIDER_THREAD,),
    )
    con.commit()
    con.close()

    repo = Repository(db)
    scoped_email = f"gmail_{account_id}_1a076e26cf3a3533"
    scoped_thread = scoped_thread_id(account_id, PROVIDER_THREAD)

    row = repo.con.execute(
        "SELECT thread_id, provider_message_id FROM emails WHERE id=?",
        (scoped_email,),
    ).fetchone()
    assert row["thread_id"] == scoped_thread
    assert row["provider_message_id"] == "1a076e26cf3a3533"

    task = repo.task("task-1")
    assert task.source_email_id == scoped_email
    assert task.source_thread_id == scoped_thread

    # Thread queries resolve through the new identity.
    assert [e.id for e in repo.emails_by_thread(scoped_thread, account_id)] == [scoped_email]
    assert [t.id for t in repo.tasks_by_thread(scoped_thread, account_id)] == ["task-1"]


def test_task_fingerprint_dual_form_dedupe():
    """Post-migration derivation must not duplicate pre-migration tasks."""
    account = "gmail_a@example.com"
    scoped = scoped_thread_id(account, PROVIDER_THREAD)
    action = _normalize_action("Send the Q3 plan")

    current = task_fingerprint(scoped, action)
    legacy = task_fingerprint(PROVIDER_THREAD, action)
    assert current != legacy

    candidates = candidate_fingerprints(scoped, account, action)
    assert current in candidates
    assert legacy in candidates
    # A task stored under the legacy fingerprint counts as existing.
    assert legacy in candidates


def test_strip_scope_rejects_foreign_ids():
    with pytest.raises(ValueError):
        strip_scope("gmail_gmail_a@example.com_abc123def45", "gmail_b@example.com")
    assert strip_scope(
        "gmail_gmail_a@example.com_abc123def45", "gmail_a@example.com") == "abc123def45"


def test_rebuild_after_thread_migration_keeps_single_task(tmp_path):
    """Legacy v2 task (raw-thread fp) -> migrate -> rebuild -> one task."""
    import sqlite3
    from backend.app.db.database import SCHEMA, INDEXES
    from backend.app.schemas import EmailAnalysis, Priority, Category
    from backend.app.services.task_derivation import rebuild_tasks_from_analyses

    db = tmp_path / "legacy_tasks.db"
    con = sqlite3.connect(db)
    con.executescript(SCHEMA)
    con.executescript(INDEXES)

    account = "gmail_a@example.com"
    email = Email(
        id="1a076e26cf3a3533", account_id=account, thread_id=PROVIDER_THREAD,
        sender="boss@work.com", subject="Q3 planning needed",
        body="Please send the Q3 plan by Friday.",
        label_ids=["INBOX"],
        source_metadata={"gmail_raw": {"labelIds": ["INBOX"], "threadId": PROVIDER_THREAD}},
    )
    con.execute(
        "INSERT INTO emails (id, payload, content_hash, imported_at, account_id, thread_id) "
        "VALUES (?,?,?,?,?,?)",
        ("1a076e26cf3a3533", email.model_dump_json(), "fp",
         "2026-01-01T00:00:00", account, PROVIDER_THREAD),
    )
    analysis = EmailAnalysis(
        short_summary="Plan request", category=Category.work,
        priority=Priority.high, priority_score=78,
        reason_for_priority="Direct request", needs_reply=True,
        action_items=[{"description": "Send the Q3 plan", "owner": "user", "deadline": "Friday"}],
        deadlines=[],
    )
    con.execute(
        "INSERT INTO email_analysis (email_id, content_hash, model_name, schema_version, payload, analyzed_at) "
        "VALUES (?,?,?,?,?,?)",
        ("1a076e26cf3a3533", "fp", "test-model", "1",
         analysis.model_dump_json(), "2026-01-01T00:00:00"),
    )
    # Legacy v2 task derived pre-migration (raw-thread fingerprint).
    legacy_fp = task_fingerprint(
        PROVIDER_THREAD, _normalize_action("Send the Q3 plan"))
    con.execute(
        "INSERT INTO tasks (id, source_email_id, source_thread_id, title, status, "
        "derivation_version, fingerprint) VALUES (?,?,?,?,?,?,?)",
        (f"task_{legacy_fp}", "1a076e26cf3a3533", PROVIDER_THREAD,
         "Send the Q3 plan", "pending", "2", legacy_fp),
    )
    con.commit()
    con.close()

    repo = Repository(db)  # migration scopes ids + threads + payloads
    scoped = scoped_email_id(account, "1a076e26cf3a3533")
    assert repo.email(scoped).thread_id == scoped_thread_id(account, PROVIDER_THREAD)

    added = rebuild_tasks_from_analyses(repo, "test-model")
    remaining = repo.tasks_by_email(scoped)
    assert len(remaining) == 1
    assert remaining[0].title == "Send the Q3 plan"
    assert added == 0  # nothing new derived — the legacy task covered it


def test_migrated_payload_consistency_and_draft_context(tmp_path, monkeypatch, provider):
    """Legacy DB -> migrate -> payload/columns agree -> REAL draft endpoint
    returns same-account thread context (not just fresh normalizations)."""
    import json as _json
    import sqlite3
    import importlib

    db = tmp_path / "legacy_draft.db"
    con = sqlite3.connect(db)
    from backend.app.db.database import SCHEMA, INDEXES
    con.executescript(SCHEMA)
    con.executescript(INDEXES)

    def legacy_email(raw_id, account, subject, sender="a@example.com"):
        email = Email(
            id=raw_id, account_id=account, thread_id=PROVIDER_THREAD,
            sender=sender, subject=subject, body=f"Body of {subject}",
            label_ids=["INBOX"],
            source_metadata={"gmail_raw": {"labelIds": ["INBOX"], "threadId": PROVIDER_THREAD}},
        )
        con.execute(
            "INSERT INTO emails (id, payload, content_hash, imported_at, account_id, thread_id) "
            "VALUES (?,?,?,?,?,?)",
            (raw_id, email.model_dump_json(), "fp", "2026-01-01T00:00:00",
             account, PROVIDER_THREAD),
        )

    # Account A: two messages sharing one provider thread. Account B: one
    # message with the SAME provider thread id.
    legacy_email("1a076e26cf3a3533", "gmail_a@example.com", "A first")
    legacy_email("1a07b61f84a314c5", "gmail_a@example.com", "A second")
    legacy_email("1a07c0887249fb9e", "gmail_b@example.com", "B only")
    con.commit()
    con.close()

    monkeypatch.setenv("ALFRED_RUNTIME_TOKEN", "test-secret-token-123")
    monkeypatch.setenv("ALFRED_DATABASE_PATH", str(db))
    from backend.app import config as config_mod
    from backend.app import main as main_mod
    importlib.reload(config_mod)
    importlib.reload(main_mod)
    try:
        repo = main_mod.repo
        scoped_a1 = scoped_email_id("gmail_a@example.com", "1a076e26cf3a3533")
        scoped_thread_a = scoped_thread_id("gmail_a@example.com", PROVIDER_THREAD)

        # Payload/column source-of-truth invariant after migration.
        migrated = repo.email(scoped_a1)
        assert migrated is not None
        assert migrated.id == scoped_a1
        assert migrated.thread_id == scoped_thread_a
        assert migrated.provider_message_id == "1a076e26cf3a3533"
        assert migrated.account_id == "gmail_a@example.com"

        captured: dict = {}

        async def fake_draft(email, thread_emails=None):
            captured["subjects"] = sorted(e.subject for e in (thread_emails or []))
            return "draft text"

        main_mod.ai.draft_reply = fake_draft  # type: ignore[method-assign]
        client = TestClient(main_mod.app)
        r = client.post(
            f"/api/emails/{scoped_a1}/draft",
            headers={"X-Alfred-Token": "test-secret-token-123"},
        )
        assert r.status_code == 200
        # Both same-account historical messages, never B's content.
        assert captured["subjects"] == ["A first", "A second"]
    finally:
        monkeypatch.delenv("ALFRED_RUNTIME_TOKEN")
        monkeypatch.delenv("ALFRED_DATABASE_PATH")
        importlib.reload(config_mod)
        importlib.reload(main_mod)
