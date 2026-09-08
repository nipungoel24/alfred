"""Tests for account-scoped identity and the legacy-ID migration.

Covers:
- canonical scoped id generation/parsing (including underscore emails)
- migration of a legacy single-account database: same counts, FKs
  intact (analysis/tasks/jobs), FTS reindexed, idempotent re-runs,
  backup file created
"""
import json
import sqlite3
from pathlib import Path

import pytest

from backend.app.db.database import connect, SCHEMA, INDEXES, FTS_SCHEMA
from backend.app.mail.identity import (
    scoped_email_id, parse_email_id, provider_message_id, is_scoped_for,
)
from backend.app.db.repositories import Repository
from backend.app.schemas import Email, EmailAnalysis, Priority, Category


def test_identity_round_trip():
    assert scoped_email_id("gmail_alice@example.com", "abc123def45") == "gmail_gmail_alice@example.com_abc123def45"
    assert parse_email_id("gmail_gmail_alice@example.com_abc123def45") == ("gmail_alice@example.com", "abc123def45")
    assert provider_message_id("gmail_gmail_alice@example.com_abc123def45") == "abc123def45"


def test_identity_underscore_email():
    """Account local-parts may contain underscores — parsing must survive."""
    account = "gmail_first_last@example.com"
    scoped = scoped_email_id(account, "abc123def45")
    assert parse_email_id(scoped) == (account, "abc123def45")
    assert is_scoped_for(scoped, account)
    assert not is_scoped_for(scoped, "gmail_other@example.com")


def test_identity_legacy_raw_id_not_scoped():
    assert parse_email_id("1a076e26cf3a3533") == (None, None)
    assert parse_email_id("csv-imported-1") == (None, None)


def test_identity_double_prefix_never_scopes_twice():
    """An already-scoped id round-trips, so re-scoping is impossible."""
    account = "gmail_alice@example.com"
    scoped = scoped_email_id(account, "abc123def45")
    parsed_account, raw = parse_email_id(scoped)
    assert parsed_account == account
    assert raw == "abc123def45"
    # The canonical constructor is idempotent on the raw id only —
    # re-running migration logic compares parse_email_id(id)[0] == account.
    assert parse_email_id(scoped)[0] == account


def _legacy_payload(raw_id: str, account_id: str, subject: str) -> str:
    email = Email(
        id=raw_id, account_id=account_id, sender="a@example.com",
        subject=subject, body="body text", label_ids=["INBOX"],
        source_metadata={"gmail_raw": {"labelIds": ["INBOX", "CATEGORY_PRIMARY"]}},
    )
    return email.model_dump_json()


def test_migration_rekeys_legacy_database(tmp_path: Path):
    """Old raw-Gmail-ID database migrates losslessly."""
    db = tmp_path / "legacy.sqlite3"
    con = sqlite3.connect(db)
    con.executescript(SCHEMA)
    con.executescript(INDEXES)
    con.executescript(FTS_SCHEMA)

    account_id = "gmail_nipun@example.com"
    raw_a, raw_b = "1a076e26cf3a3533", "1a07b61f84a314c5"

    for raw, subject in ((raw_a, "First"), (raw_b, "Second")):
        con.execute(
            "INSERT INTO emails (id, payload, content_hash, imported_at, account_id) "
            "VALUES (?,?,?,?,?)",
            (raw, _legacy_payload(raw, account_id, subject), "fp", "2026-01-01T00:00:00", account_id),
        )
    # FKs: analysis, task, job — all keyed by the legacy raw id
    analysis_payload = EmailAnalysis(
        short_summary="s", category=Category.work, priority=Priority.high,
        priority_score=70, reason_for_priority="r", needs_reply=False,
    ).model_dump_json()
    con.execute(
        "INSERT INTO email_analysis (email_id, content_hash, model_name, schema_version, payload, analyzed_at) "
        "VALUES (?,?,?,?,?,?)",
        (raw_a, "fp", "test-model", "1", analysis_payload, "2026-01-01T00:00:00"),
    )
    con.execute(
        "INSERT INTO tasks (id, source_email_id, title, status) VALUES ('task-1', ?, 'Do thing', 'pending')",
        (raw_a,),
    )
    con.execute(
        "INSERT INTO jobs (id, job_type, target_id, status, created_at) VALUES (?, 'analyze_email', ?, 'queued', '2026-01-01T00:00:00')",
        (f"analyze_{raw_a}", raw_a),
    )
    # Populate FTS with legacy content
    con.executescript(
        "INSERT INTO emails_fts(rowid, subject, sender, body) "
        "SELECT rowid, subject_col, sender_col, json_extract(payload, '$.body') FROM emails"
    )
    con.commit()
    con.close()

    # Reconnect through the production path — migration runs on connect()
    repo = Repository(db)

    scoped_a = scoped_email_id(account_id, raw_a)
    scoped_b = scoped_email_id(account_id, raw_b)

    # Same number of emails, new keys
    assert repo.email_count() == 2
    assert repo.email_exists(scoped_a)
    assert repo.email_exists(scoped_b)
    assert not repo.email_exists(raw_a)

    # Payload id agrees with the primary key
    assert repo.email(scoped_a).id == scoped_a

    # Analyses/tasks/jobs still connected
    assert repo.cached_analysis(scoped_a, "fp", "test-model") is not None
    assert repo.tasks_by_email(scoped_a)[0].title == "Do thing"
    assert repo.job(f"analyze_{scoped_a}")["target_id"] == scoped_a

    # Search works through FTS after migration
    results = repo.search_emails("First")
    assert len(results) == 1
    assert results[0].id == scoped_a

    # Backup file exists (created before re-keying)
    assert (tmp_path / "legacy.sqlite3.pre_id_migration.bak").exists()


def test_migration_is_idempotent(tmp_path: Path):
    """Re-running connect() must not re-scope or double-prefix ids."""
    db = tmp_path / "idem.sqlite3"
    account_id = "gmail_under_score@example.com"
    repo = Repository(db)
    email = Email(
        id="1a076e26cf3a3533", account_id=account_id,
        sender="a@example.com", subject="Hi", body="body",
    )
    repo.upsert_email_commit(email, "fp")
    repo.close()

    # Reconnect: migration runs and scopes the raw id.
    repo2 = Repository(db)
    scoped = scoped_email_id(account_id, "1a076e26cf3a3533")
    assert repo2.email_exists(scoped)
    repo2.close()

    # Third connection: nothing to migrate, nothing double-prefixed.
    repo3 = Repository(db)
    assert repo3.email_exists(scoped)
    assert repo3.email_count() == 1
    double = repo3.con.execute(
        "SELECT COUNT(*) FROM emails WHERE id LIKE ?",
        (f"gmail_{account_id}_gmail_%",),
    ).fetchone()[0]
    assert double == 0


def test_backup_is_readable_snapshot(tmp_path: Path):
    """The pre-migration backup opens cleanly and holds pre-migration data."""
    import sqlite3

    db = tmp_path / "snap.sqlite3"
    account_id = "gmail_alice@example.com"
    repo = Repository(db)
    repo.upsert_email_commit(
        Email(id="1a076e26cf3a3533", account_id=account_id,
              sender="a@example.com", subject="Hi", body="body"), "fp")
    repo.close()

    Repository(db).close()  # triggers migration + backup
    backup = tmp_path / "snap.sqlite3.pre_id_migration.bak"
    assert backup.exists() and backup.stat().st_size > 0

    bak = sqlite3.connect(backup)
    try:
        assert bak.execute("SELECT COUNT(*) FROM emails").fetchone()[0] == 1
        row = bak.execute("SELECT id, account_id FROM emails").fetchone()
        assert row[0] == "1a076e26cf3a3533"  # raw pre-migration id
        assert row[1] == account_id
        payload = json.loads(bak.execute("SELECT payload FROM emails").fetchone()[0])
        assert payload["subject"] == "Hi"
    finally:
        bak.close()


def test_backup_failure_aborts_migration(tmp_path: Path):
    """When no consistent snapshot can be written, ids stay untouched."""
    db = tmp_path / "abort.sqlite3"
    repo = Repository(db)
    repo.upsert_email_commit(
        Email(id="1a076e26cf3a3533", account_id="gmail_alice@example.com",
              sender="a@example.com", subject="Hi", body="body"), "fp")
    repo.close()

    # Poison the backup path: a directory where the backup file must go.
    backup = tmp_path / "abort.sqlite3.pre_id_migration.bak"
    backup.mkdir()

    repo2 = Repository(db)  # migration must abort, not corrupt
    try:
        assert repo2.email_exists("1a076e26cf3a3533")
        assert repo2.email_count() == 1
    finally:
        repo2.close()
        backup.rmdir()

    # With the path clear, the next connect migrates normally.
    repo3 = Repository(db)
    assert repo3.email_exists(
        scoped_email_id("gmail_alice@example.com", "1a076e26cf3a3533"))


def test_provider_uniqueness_enforced(tmp_path: Path):
    """Duplicate (account_id, provider_message_id) rows are rejected."""
    import sqlite3

    repo = Repository(tmp_path / "test.sqlite3")
    account = "gmail_alice@example.com"
    repo.upsert_email_commit(
        Email(id=scoped_email_id(account, "abc123def45"), account_id=account,
              provider_message_id="abc123def45",
              sender="a@example.com", subject="One", body="b"), "fp1")
    with pytest.raises(sqlite3.IntegrityError):
        repo.con.execute(
            "INSERT INTO emails (id, payload, content_hash, imported_at, "
            "account_id, provider_message_id) VALUES (?,?,?,?,?,?)",
            ("gmail_other_row", "{}", "fp", "2026-01-01T00:00:00",
             account, "abc123def45"),
        )


def test_null_provider_rows_exempt_from_uniqueness(tmp_path: Path):
    """Legacy/CSV rows with NULL provider ids never collide."""
    repo = Repository(tmp_path / "test.sqlite3")
    for i in range(3):
        repo.upsert_email_commit(
            Email(id=f"csv-{i}", sender="a@example.com",
                  subject=f"S{i}", body="b"), "fp")
    assert repo.email_count() == 3
