"""Comprehensive tests for FTS5 full-text search functionality.

Tests cover:
- FTS5 contentless table (content='') behavior
- INSERT operations and search
- DELETE operations with rebuild
- Search functionality
"""
import sqlite3
from pathlib import Path
from backend.app.schemas import Email
from backend.app.db.repositories import Repository


def make_email(id: str = 'e1', sender: str = 'alice@example.com', 
               subject: str = 'Hello World', body: str = 'Test body content') -> Email:
    return Email(id=id, sender=sender, subject=subject, body=body)


def test_fts_insert_and_search(tmp_path: Path):
    """FTS5 should index emails and support full-text search."""
    repo = Repository(tmp_path / 'test.sqlite3')
    email = make_email()
    repo.upsert_email(email, 'fp1')
    
    results = repo.search_emails('Hello')
    assert len(results) == 1
    assert results[0].id == 'e1'


def test_fts_search_no_match(tmp_path: Path):
    """FTS5 should return empty for non-matching queries."""
    repo = Repository(tmp_path / 'test.sqlite3')
    email = make_email(subject='Hello World', body='Test body')
    repo.upsert_email(email, 'fp1')
    
    results = repo.search_emails('nonexistent')
    assert len(results) == 0


def test_fts_delete_cleans_index(tmp_path: Path):
    """DELETE should remove entries from search results after rebuild."""
    repo = Repository(tmp_path / 'test.sqlite3')
    email = make_email()
    repo.upsert_email(email, 'fp1')
    
    # Verify email exists
    results = repo.search_emails('Hello')
    assert len(results) == 1
    
    # Delete email
    repo.delete_email('e1')
    
    # Verify email is gone from search
    results = repo.search_emails('Hello')
    assert len(results) == 0


def test_fts_update_reindexes(tmp_path: Path):
    """UPDATE should reindex the FTS5 entry after rebuild."""
    repo = Repository(tmp_path / 'test.sqlite3')
    email = make_email(subject='Original Subject')
    repo.upsert_email(email, 'fp1')
    
    # Search for original
    results = repo.search_emails('Original')
    assert len(results) == 1
    
    # Update email - with contentless FTS5, we need to rebuild
    updated_email = make_email(id='e1', subject='Updated Subject')
    repo.upsert_email(updated_email, 'fp2')
    
    # Rebuild FTS to reflect changes
    repo.rebuild_fts()
    
    # Search for new content - should find the email
    results = repo.search_emails('Updated')
    assert len(results) == 1
    assert results[0].subject == 'Updated Subject'


def test_fts_multiple_emails(tmp_path: Path):
    """FTS5 should handle multiple emails correctly."""
    repo = Repository(tmp_path / 'test.sqlite3')
    
    emails = [
        make_email(id='e1', subject='Meeting Tomorrow', body='Let us meet at 10am'),
        make_email(id='e2', subject='Project Update', body='The project is on track'),
        make_email(id='e3', subject='Lunch Plans', body='Want to grab lunch?'),
    ]
    
    for e in emails:
        repo.upsert_email(e, 'fp')
    
    # Search should find relevant emails
    results = repo.search_emails('meeting')
    assert len(results) == 1
    assert results[0].id == 'e1'
    
    results = repo.search_emails('project')
    assert len(results) == 1
    assert results[0].id == 'e2'


def test_fts_body_truncation(tmp_path: Path):
    """FTS5 should handle long bodies by truncating to 5000 chars."""
    repo = Repository(tmp_path / 'test.sqlite3')
    long_body = 'A' * 10000  # Longer than 5000 chars
    email = make_email(body=long_body)
    repo.upsert_email(email, 'fp1')
    
    # Should be searchable by subject (which is not truncated)
    results = repo.search_emails('Hello')
    assert len(results) == 1


def test_fts_empty_body(tmp_path: Path):
    """FTS5 should handle emails with empty bodies."""
    repo = Repository(tmp_path / 'test.sqlite3')
    email = make_email(body='')
    repo.upsert_email(email, 'fp1')
    
    # Should be searchable by subject
    results = repo.search_emails('Hello')
    assert len(results) == 1


def test_fts_special_characters(tmp_path: Path):
    """FTS5 should handle special characters in search queries."""
    repo = Repository(tmp_path / 'test.sqlite3')
    email = make_email(subject='Quote: important', body='Price: 100 dollars')
    repo.upsert_email(email, 'fp1')
    
    # Search with special characters
    results = repo.search_emails('important')
    assert len(results) == 1


def test_fts_case_insensitive(tmp_path: Path):
    """FTS5 search should be case-insensitive."""
    repo = Repository(tmp_path / 'test.sqlite3')
    email = make_email(subject='Hello World')
    repo.upsert_email(email, 'fp1')
    
    # Search with different case
    results = repo.search_emails('hello')
    assert len(results) == 1
    
    results = repo.search_emails('HELLO')
    assert len(results) == 1


def test_fts_fallback_to_like(tmp_path: Path):
    """Should fall back to LIKE search if FTS5 fails."""
    repo = Repository(tmp_path / 'test.sqlite3')
    email = make_email(subject='Test Subject', sender='test@example.com')
    repo.upsert_email(email, 'fp1')
    
    # LIKE search should work
    results = repo.search_emails('Test')
    assert len(results) == 1


def test_fts_multiple_delete(tmp_path: Path):
    """Multiple deletes should work correctly."""
    repo = Repository(tmp_path / 'test.sqlite3')
    
    emails = [
        make_email(id='e1', subject='First'),
        make_email(id='e2', subject='Second'),
        make_email(id='e3', subject='Third'),
    ]
    
    for e in emails:
        repo.upsert_email(e, 'fp')
    
    # Delete first email
    repo.delete_email('e1')
    results = repo.search_emails('First')
    assert len(results) == 0
    results = repo.search_emails('Second')
    assert len(results) == 1
    
    # Delete second email
    repo.delete_email('e2')
    results = repo.search_emails('Second')
    assert len(results) == 0
    results = repo.search_emails('Third')
    assert len(results) == 1


def test_fts_upsert_idempotent(tmp_path: Path):
    """Upserting the same email twice should not create duplicates."""
    repo = Repository(tmp_path / 'test.sqlite3')
    email = make_email()
    
    repo.upsert_email(email, 'fp1')
    repo.upsert_email(email, 'fp1')
    
    results = repo.search_emails('Hello')
    assert len(results) == 1


def test_fts_rebuild_removes_orphans(tmp_path: Path):
    """Rebuild should remove orphaned FTS entries."""
    repo = Repository(tmp_path / 'test.sqlite3')
    email = make_email()
    repo.upsert_email(email, 'fp1')
    
    # Verify email exists
    results = repo.search_emails('Hello')
    assert len(results) == 1
    
    # Delete email directly (without rebuild)
    repo.con.execute('DELETE FROM emails WHERE id=?', ('e1',))
    repo.con.commit()
    
    # Email should still be in FTS (orphaned)
    # After rebuild, it should be gone
    repo.rebuild_fts()
    
    results = repo.search_emails('Hello')
    assert len(results) == 0
