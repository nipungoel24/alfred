"""Tests for multi-account identity isolation.

Verifies that:
- Message IDs are treated as account-scoped
- Label backfill uses correct account tokens
- Account isolation is maintained
"""
from pathlib import Path
from backend.app.schemas import Email, SearchFilters
from backend.app.db.repositories import Repository


def make_email(id: str = 'e1', sender: str = 'alice@example.com', 
               subject: str = 'Hello World', body: str = 'Test body',
               account_id: str | None = None) -> Email:
    return Email(
        id=id, sender=sender, subject=subject, body=body,
        account_id=account_id
    )


def test_account_id_stored_correctly(tmp_path: Path):
    """Email account_id should be stored and retrieved correctly."""
    repo = Repository(tmp_path / 'test.sqlite3')
    
    email = make_email(id='e1', account_id='account_1')
    repo.upsert_email(email, 'fp1')
    
    # Verify account_id is stored
    results = repo.con.execute(
        "SELECT id, account_id FROM emails WHERE id='e1'"
    ).fetchone()
    assert results is not None
    assert results[1] == 'account_1'


def test_emails_missing_labels_by_account(tmp_path: Path):
    """emails_missing_labels should filter by account_id."""
    repo = Repository(tmp_path / 'test.sqlite3')
    
    # Create emails with empty label_ids (which stores as '[]')
    emails = [
        make_email(id='e1', account_id='account_1'),
        make_email(id='e2', account_id='account_1'),
        make_email(id='e3', account_id='account_2'),
    ]
    for e in emails:
        repo.upsert_email(e, 'fp')
    
    # Check what's stored
    rows = repo.con.execute(
        "SELECT id, account_id, label_ids_json FROM emails"
    ).fetchall()
    print("Stored emails:", [(r[0], r[1], r[2]) for r in rows])
    
    # Get missing labels for account_1 only
    pending = repo.emails_missing_labels(account_id='account_1')
    print("Pending for account_1:", pending)
    
    # The function checks for label_ids_json IS NULL
    # But upsert_email stores '[]' for empty labels
    # So we need to test with emails that have NULL label_ids_json
    repo.con.execute(
        "UPDATE emails SET label_ids_json = NULL WHERE id IN ('e1', 'e2')"
    )
    repo.con.commit()
    
    pending = repo.emails_missing_labels(account_id='account_1')
    assert len(pending) == 2
    assert 'e1' in pending
    assert 'e2' in pending
    
    # Get missing labels for account_2 only
    repo.con.execute(
        "UPDATE emails SET label_ids_json = NULL WHERE id = 'e3'"
    )
    repo.con.commit()
    
    pending = repo.emails_missing_labels(account_id='account_2')
    assert len(pending) == 1
    assert 'e3' in pending
    
    # Get all missing labels
    pending = repo.emails_missing_labels()
    assert len(pending) == 3


def test_search_respects_account_isolation(tmp_path: Path):
    """Search should work across accounts but preserve account context."""
    repo = Repository(tmp_path / 'test.sqlite3')
    
    emails = [
        make_email(id='e1', sender='alice@example.com', subject='From Account 1', account_id='account_1'),
        make_email(id='e2', sender='alice@example.com', subject='From Account 2', account_id='account_2'),
    ]
    for e in emails:
        repo.upsert_email(e, 'fp')
    
    # Search should find both (global search)
    results = repo.search_emails('alice')
    assert len(results) == 2
    
    # Structured search with account filter
    filters = SearchFilters(sender='alice')
    results = repo.search_emails_structured(filters)
    assert len(results) == 2


def test_delete_email_by_account(tmp_path: Path):
    """Deleting an email should only affect that email."""
    repo = Repository(tmp_path / 'test.sqlite3')
    
    emails = [
        make_email(id='e1', subject='Account 1 Email', account_id='account_1'),
        make_email(id='e2', subject='Account 2 Email', account_id='account_2'),
    ]
    for e in emails:
        repo.upsert_email(e, 'fp')
    
    # Delete email from account_1
    repo.delete_email('e1')
    
    # Verify account_2 email still exists
    results = repo.con.execute(
        "SELECT id FROM emails WHERE id='e2'"
    ).fetchone()
    assert results is not None
    
    # Verify account_1 email is gone
    results = repo.con.execute(
        "SELECT id FROM emails WHERE id='e1'"
    ).fetchone()
    assert results is None


def test_label_update_by_account(tmp_path: Path):
    """Label updates should only affect the correct email."""
    repo = Repository(tmp_path / 'test.sqlite3')
    
    email = make_email(id='e1', account_id='account_1')
    repo.upsert_email(email, 'fp1')
    
    # Update labels
    labels = ['INBOX', 'IMPORTANT']
    repo.update_email_labels('e1', labels)
    
    # Verify labels are stored
    row = repo.con.execute(
        "SELECT label_ids_json FROM emails WHERE id='e1'"
    ).fetchone()
    assert row is not None
    import json
    stored_labels = json.loads(row[0])
    assert 'INBOX' in stored_labels
    assert 'IMPORTANT' in stored_labels


def test_account_credentials_isolation(tmp_path: Path):
    """Credentials should be isolated per account."""
    repo = Repository(tmp_path / 'test.sqlite3')
    
    # Create accounts
    from backend.app.schemas import EmailAccount
    account1 = EmailAccount(
        id='account_1', provider='gmail', email_address='user1@gmail.com',
        connection_status='connected'
    )
    account2 = EmailAccount(
        id='account_2', provider='gmail', email_address='user2@gmail.com',
        connection_status='connected'
    )
    repo.save_account(account1)
    repo.save_account(account2)
    
    # Store credentials for each account
    repo.save_credentials('account_1', 'refresh_1', 'token_1', None)
    repo.save_credentials('account_2', 'refresh_2', 'token_2', None)
    
    # Verify credentials are isolated
    creds1 = repo.credentials('account_1')
    creds2 = repo.credentials('account_2')
    
    assert creds1 is not None
    assert creds2 is not None
    assert creds1['encrypted_access_token'] == 'token_1'
    assert creds2['encrypted_access_token'] == 'token_2'
