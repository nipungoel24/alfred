"""Tests for structured search functionality."""
from pathlib import Path
from backend.app.schemas import Email, SearchFilters
from backend.app.db.repositories import Repository


def make_email(id: str = 'e1', sender: str = 'alice@example.com', 
               subject: str = 'Hello World', body: str = 'Test body',
               received_at: str = '2024-01-15T10:00:00') -> Email:
    from datetime import datetime
    return Email(
        id=id, sender=sender, subject=subject, body=body,
        received_at=datetime.fromisoformat(received_at) if received_at else None
    )


def test_structured_search_by_sender(tmp_path: Path):
    """Should filter emails by sender."""
    repo = Repository(tmp_path / 'test.sqlite3')
    
    emails = [
        make_email(id='e1', sender='alice@example.com', subject='From Alice'),
        make_email(id='e2', sender='bob@example.com', subject='From Bob'),
    ]
    for e in emails:
        repo.upsert_email(e, 'fp')
    
    filters = SearchFilters(sender='alice')
    results = repo.search_emails_structured(filters)
    assert len(results) == 1
    assert results[0].sender == 'alice@example.com'


def test_structured_search_by_subject(tmp_path: Path):
    """Should filter emails by subject."""
    repo = Repository(tmp_path / 'test.sqlite3')
    
    emails = [
        make_email(id='e1', subject='Meeting Tomorrow'),
        make_email(id='e2', subject='Project Update'),
    ]
    for e in emails:
        repo.upsert_email(e, 'fp')
    
    filters = SearchFilters(subject='meeting')
    results = repo.search_emails_structured(filters)
    assert len(results) == 1
    assert 'Meeting' in results[0].subject


def test_structured_search_by_date(tmp_path: Path):
    """Should filter emails by date range."""
    repo = Repository(tmp_path / 'test.sqlite3')
    
    emails = [
        make_email(id='e1', subject='Old Email', received_at='2023-01-15T10:00:00'),
        make_email(id='e2', subject='New Email', received_at='2024-06-15T10:00:00'),
        make_email(id='e3', subject='Future Email', received_at='2025-01-15T10:00:00'),
    ]
    for e in emails:
        repo.upsert_email(e, 'fp')
    
    # Filter after 2024-01-01
    filters = SearchFilters(after='2024-01-01')
    results = repo.search_emails_structured(filters)
    assert len(results) == 2
    
    # Filter before 2024-12-31
    filters = SearchFilters(before='2024-12-31')
    results = repo.search_emails_structured(filters)
    assert len(results) == 2
    
    # Filter between dates
    filters = SearchFilters(after='2024-01-01', before='2024-12-31')
    results = repo.search_emails_structured(filters)
    assert len(results) == 1
    assert results[0].subject == 'New Email'


def test_structured_search_combined_filters(tmp_path: Path):
    """Should apply multiple filters correctly."""
    repo = Repository(tmp_path / 'test.sqlite3')
    
    emails = [
        make_email(id='e1', sender='alice@example.com', subject='Meeting', received_at='2024-01-15T10:00:00'),
        make_email(id='e2', sender='alice@example.com', subject='Project', received_at='2024-06-15T10:00:00'),
        make_email(id='e3', sender='bob@example.com', subject='Meeting', received_at='2024-01-15T10:00:00'),
    ]
    for e in emails:
        repo.upsert_email(e, 'fp')
    
    # Filter by sender and subject
    filters = SearchFilters(sender='alice', subject='meeting')
    results = repo.search_emails_structured(filters)
    assert len(results) == 1
    assert results[0].id == 'e1'


def test_structured_search_with_free_text(tmp_path: Path):
    """Should combine free text with filters."""
    repo = Repository(tmp_path / 'test.sqlite3')
    
    emails = [
        make_email(id='e1', sender='alice@example.com', subject='Meeting Tomorrow'),
        make_email(id='e2', sender='alice@example.com', subject='Project Update'),
        make_email(id='e3', sender='bob@example.com', subject='Meeting Notes'),
    ]
    for e in emails:
        repo.upsert_email(e, 'fp')
    
    # Filter by sender and search for "meeting"
    filters = SearchFilters(sender='alice', free_text=['meeting'])
    results = repo.search_emails_structured(filters)
    assert len(results) == 1
    assert results[0].subject == 'Meeting Tomorrow'


def test_structured_search_no_results(tmp_path: Path):
    """Should return empty when no emails match."""
    repo = Repository(tmp_path / 'test.sqlite3')
    
    emails = [
        make_email(id='e1', sender='alice@example.com', subject='Hello'),
    ]
    for e in emails:
        repo.upsert_email(e, 'fp')
    
    filters = SearchFilters(sender='bob')
    results = repo.search_emails_structured(filters)
    assert len(results) == 0


def test_structured_search_limit(tmp_path: Path):
    """Should respect limit parameter."""
    repo = Repository(tmp_path / 'test.sqlite3')
    
    emails = [
        make_email(id=f'e{i}', sender='alice@example.com', subject=f'Email {i}')
        for i in range(20)
    ]
    for e in emails:
        repo.upsert_email(e, 'fp')
    
    filters = SearchFilters(sender='alice')
    results = repo.search_emails_structured(filters, limit=5)
    assert len(results) == 5


def test_filter_before_limit(tmp_path: Path):
    """Priority and needs_reply filters must be applied BEFORE LIMIT/OFFSET.

    If we fetch 200 emails and then filter in Python, we might get 0 results
    even though there are matching emails beyond the 200 window. The SQL must
    filter first, then paginate.
    """
    repo = Repository(tmp_path / 'test.sqlite3')

    # Create 10 emails, only 1 has high priority
    for i in range(10):
        e = make_email(id=f'e{i}', subject=f'Email {i}',
                       received_at=f'2024-01-{10+i:02d}T10:00:00')
        repo.upsert_email(e, 'fp')

    # Manually set analysis with different priorities
    from backend.app.schemas import EmailAnalysis, Priority, Category
    for i in range(10):
        analysis = EmailAnalysis(
            short_summary=f'Summary {i}',
            category=Category.work,
            priority=Priority.high if i == 5 else Priority.low,
            priority_score=90 if i == 5 else 10,
            reason_for_priority='Test',
            needs_reply=(i == 3),
        )
        repo.save_analysis(f'e{i}', 'fp', 'test-model', analysis)

    # Filter for high priority with limit=3 — should find the 1 high-priority email
    # even though it's email #6 (index 5) in the list
    filtered = repo.emails_filtered(priority='high', limit=3)
    assert len(filtered) == 1
    assert filtered[0].id == 'e5'

    # Filter for needs_reply with limit=2 — should find the 1 needs-reply email
    filtered = repo.emails_filtered(needs_reply=True, limit=2)
    assert len(filtered) == 1
    assert filtered[0].id == 'e3'


def test_account_scoped_structured_search(tmp_path: Path):
    """Structured search must respect account_id filter."""
    repo = Repository(tmp_path / 'test.sqlite3')

    emails = [
        make_email(id='e1', sender='alice@example.com', subject='Account A email'),
        make_email(id='e2', sender='alice@example.com', subject='Account B email'),
    ]
    emails[0].account_id = 'acct_a'
    emails[1].account_id = 'acct_b'
    for e in emails:
        repo.upsert_email(e, 'fp')

    # Search scoped to account_a
    filters = SearchFilters(sender='alice')
    results = repo.search_emails_structured(filters, account_id='acct_a')
    assert len(results) == 1
    assert results[0].account_id == 'acct_a'

    # Search scoped to account_b
    results = repo.search_emails_structured(filters, account_id='acct_b')
    assert len(results) == 1
    assert results[0].account_id == 'acct_b'
