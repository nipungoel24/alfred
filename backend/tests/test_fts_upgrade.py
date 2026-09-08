"""FTS schema upgrade + safe MATCH compilation.

Covers P0-3 and P2:
- legacy contentless (no contentless_delete) databases upgrade explicitly
  through production connect(): update/delete work with no manual rebuild,
  results survive close/reopen
- capability fallback path (old SQLite) uses the legacy schema + rebuilds
- free text compiles to literal FTS terms (quotes/parens/hyphens/colons/
  OR/NEAR/asterisks/malformed quotes never become FTS syntax)
"""
import sqlite3
from pathlib import Path

import pytest

from backend.app.db.database import (
    connect, fts_delete_supported, fts_table_uses_contentless_delete,
)
from backend.app.db.repositories import Repository
from backend.app.db.search_query import compile_fts_match
from backend.app.schemas import Email, SearchFilters


LEGACY_FTS = """
CREATE VIRTUAL TABLE emails_fts USING fts5(
    subject,
    sender,
    body,
    content='',
    tokenize='unicode61'
);
"""


def make_email(id: str = "e1", subject: str = "Hello World",
               body: str = "Test body", account_id: str | None = None) -> Email:
    return Email(id=id, sender="alice@example.com", subject=subject,
                 body=body, account_id=account_id)


def test_legacy_fts_schema_upgrades_through_connect(tmp_path: Path):
    """Full 10-step legacy upgrade regression through production connect()."""
    from backend.app.db.database import SCHEMA, INDEXES

    db = tmp_path / "legacy_fts.sqlite3"
    # 1. database with Alfred's OLD contentless FTS schema
    con = sqlite3.connect(db)
    con.executescript(SCHEMA)
    con.executescript(INDEXES)
    con.executescript(LEGACY_FTS)
    # 2. indexed mail (columns filled as upsert_email would)
    con.execute(
        "INSERT INTO emails (id, payload, content_hash, imported_at, "
        "mailbox_state, subject_col, sender_col) VALUES (?,?,?,?,?,?,?)",
        ("e1", make_email().model_dump_json(), "fp",
         "2026-01-01T00:00:00", "active_inbox", "Hello World",
         "alice@example.com"),
    )
    con.execute(
        "INSERT INTO emails_fts(rowid, subject, sender, body) "
        "SELECT rowid, subject_col, sender_col, json_extract(payload, '$.body') "
        "FROM emails"
    )
    con.commit()
    # 3. close database
    con.close()

    # 4. open through CURRENT production connect()
    repo = Repository(db)
    assert fts_table_uses_contentless_delete(repo.con) is True

    # 5. update an email WITHOUT manual rebuild
    repo.upsert_email_commit(
        make_email(subject="Updated Quarterly Report", body="Brand new body"), "fp2")

    # 6. old terms disappear
    assert repo.search_emails("Hello") == []
    # 7. new terms appear
    assert [e.id for e in repo.search_emails("Quarterly")] == ["e1"]

    # 8. delete works
    repo.delete_email("e1")
    assert repo.search_emails("Quarterly") == []
    assert repo.search_emails("Brand") == []

    # 9. close/reopen — 10. results remain correct
    repo.close()
    repo2 = Repository(db)
    assert repo2.search_emails("Quarterly") == []
    assert fts_table_uses_contentless_delete(repo2.con) is True


def test_capability_probe_is_isolated(tmp_path: Path):
    """The probe must not touch the production table name."""
    db = tmp_path / "probe.sqlite3"
    repo = Repository(db)
    assert repo.con.execute(
        "SELECT name FROM sqlite_master WHERE name='alfred_fts_cap_probe'"
    ).fetchone() is None
    assert fts_delete_supported(repo.con) is True


def test_existing_schema_detection(tmp_path: Path):
    from backend.app.db.database import SCHEMA

    db = tmp_path / "detect.sqlite3"
    con = sqlite3.connect(db)
    con.executescript(SCHEMA)
    con.executescript(LEGACY_FTS)
    assert fts_table_uses_contentless_delete(con) is False
    con.close()

    repo = Repository(db)
    assert fts_table_uses_contentless_delete(repo.con) is True


def test_old_sqlite_fallback_path(tmp_path: Path, monkeypatch):
    """Simulated incapable runtime: legacy schema + rebuild maintenance."""
    import backend.app.db.database as db_mod

    monkeypatch.setattr(db_mod, "fts_delete_supported", lambda con: False)
    # repositories.py imported the name directly — patch there too.
    import backend.app.db.repositories as repo_mod
    monkeypatch.setattr(repo_mod, "fts_delete_supported", lambda con: False)

    db = tmp_path / "fallback.sqlite3"
    repo = Repository(db)
    assert fts_table_uses_contentless_delete(repo.con) is False

    repo.upsert_email_commit(make_email(), "fp1")
    assert len(repo.search_emails("Hello")) == 1
    repo.upsert_email_commit(
        make_email(subject="Changed", body="Changed body"), "fp2")
    assert repo.search_emails("Hello") == []
    assert len(repo.search_emails("Changed")) == 1
    repo.delete_email("e1")
    assert repo.search_emails("Changed") == []


# ── FTS literal compilation ──

def test_compile_plain_words():
    assert compile_fts_match(["hello", "world"]) == '"hello" "world"'


def test_compile_empty():
    assert compile_fts_match([]) is None
    assert compile_fts_match(["   "]) is None
    assert compile_fts_match(None) is None


@pytest.mark.parametrize("word,expected", [
    ("OR", '"OR"'),
    ("NEAR", '"NEAR"'),
    ("(hello)", '"(hello)"'),
    ("well-known", '"well-known"'),
    ("from:alice", '"from:alice"'),
    ("*.pdf", '"*.pdf"'),
    ('say "hi"', '"say ""hi"""'),
    ('"unbalanced', '"""unbalanced"'),
    ("C++", '"C++"'),
])
def test_compile_special_characters_stay_literal(word, expected):
    assert compile_fts_match([word]) == expected


def test_special_characters_search_literally(tmp_path: Path):
    repo = Repository(tmp_path / "test.sqlite3")
    repo.upsert_email_commit(
        make_email(subject="C++ OR (Rust) review: well-known *.pdf"), "fp1")

    # An FTS operator typed by the user must not change meaning or crash.
    assert len(repo.search_emails("OR")) == 1
    assert len(repo.search_emails("C++")) == 1
    assert len(repo.search_emails("(Rust)")) == 1
    assert len(repo.search_emails("*.pdf")) == 1
    assert len(repo.search_emails('review:')) == 1
    # Structured path compiles too.
    assert len(repo.search_emails_structured(
        SearchFilters(free_text=["OR", "well-known"]))) == 1
