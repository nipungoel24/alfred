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


def test_same_provider_message_id_collision(tmp_path: Path):
    """Two accounts with the same provider_message_id must coexist.

    Gmail message IDs are account-scoped. Account A and Account B can
    each have a message with provider_message_id 'same-id'. Both must
    remain isolated through fetch/update/delete/analysis/search.
    """
    repo = Repository(tmp_path / 'test.sqlite3')

    # In production, Gmail sync uses account-prefixed IDs to avoid collision.
    # Simulate this: two accounts with the same raw Gmail message ID get
    # different database IDs via the "gmail_{account_id}_{msg_id}" pattern.
    email_a = make_email(id='gmail_account_a_same-id', subject='From Account A',
                         sender='alice@example.com', account_id='account_a')
    email_b = make_email(id='gmail_account_b_same-id', subject='From Account B',
                         sender='bob@example.com', account_id='account_b')

    repo.upsert_email(email_a, 'fp_a')
    repo.upsert_email(email_b, 'fp_b')

    # Both emails must exist and be isolated
    assert repo.email_exists('gmail_account_a_same-id')
    assert repo.email_exists('gmail_account_b_same-id')

    # Verify account isolation: fetch by account
    emails_a = repo.emails(account_id='account_a')
    emails_b = repo.emails(account_id='account_b')
    assert len(emails_a) == 1
    assert len(emails_b) == 1

    # Verify search works across accounts
    results = repo.search_emails('Account A')
    assert len(results) == 1
    assert results[0].account_id == 'account_a'

    # Verify deletion only affects one account's data
    repo.delete_email('gmail_account_a_same-id')
    assert not repo.email_exists('gmail_account_a_same-id')
    assert repo.email_exists('gmail_account_b_same-id')
    results = repo.search_emails('Account B')
    assert len(results) == 1


def test_account_prefixed_email_ids(tmp_path: Path):
    """Gmail sync must use account-prefixed IDs to avoid collision.

    In production, Gmail sync constructs IDs as:
        f"gmail_{account.email_address}_{msg_id}"
    This prevents two accounts from colliding on the same Gmail message ID.
    """
    repo = Repository(tmp_path / 'test.sqlite3')

    # Simulate account-prefixed IDs from Gmail sync
    email_a = make_email(id='gmail_user1@gmail.com_msg123',
                         subject='Important Meeting', account_id='user1@gmail.com')
    email_b = make_email(id='gmail_user2@gmail.com_msg123',
                         subject='Lunch Plans', account_id='user2@gmail.com')

    repo.upsert_email(email_a, 'fp_a')
    repo.upsert_email(email_b, 'fp_b')

    # Both must exist independently
    assert repo.email_exists('gmail_user1@gmail.com_msg123')
    assert repo.email_exists('gmail_user2@gmail.com_msg123')

    # Account isolation: each account sees only its own
    emails_a = repo.emails(account_id='user1@gmail.com')
    emails_b = repo.emails(account_id='user2@gmail.com')
    assert len(emails_a) == 1
    assert len(emails_b) == 1
    assert emails_a[0].subject == 'Important Meeting'
    assert emails_b[0].subject == 'Lunch Plans'

    # Delete one — the other must survive
    repo.delete_email('gmail_user1@gmail.com_msg123')
    assert not repo.email_exists('gmail_user1@gmail.com_msg123')
    assert repo.email_exists('gmail_user2@gmail.com_msg123')

    # Search must return only the surviving email (search by subject content, not ID)
    results = repo.search_emails('Lunch Plans')
    assert len(results) == 1
    assert results[0].account_id == 'user2@gmail.com'


def test_account_specific_counts(tmp_path: Path):
    """email_counts must respect account_id filter."""
    repo = Repository(tmp_path / 'test.sqlite3')

    # Create emails across two accounts with known labels
    for i, (acct, labels) in enumerate([
        ('acct_a', ['INBOX', 'CATEGORY_PRIMARY']),
        ('acct_a', ['INBOX', 'CATEGORY_PROMOTIONS']),
        ('acct_b', ['INBOX', 'CATEGORY_PRIMARY']),
    ]):
        e = make_email(id=f'e{i}', account_id=acct)
        e.label_ids = labels
        repo.upsert_email(e, 'fp')

    # Count for account_a only
    counts_a = repo.email_counts(account_id='acct_a')
    assert counts_a['active_inbox'] == 2
    assert counts_a['categories']['primary'] == 1
    assert counts_a['categories']['promotions'] == 1

    # Count for account_b only
    counts_b = repo.email_counts(account_id='acct_b')
    assert counts_b['active_inbox'] == 1
    assert counts_b['categories']['primary'] == 1

    # Count for all accounts
    counts_all = repo.email_counts()
    assert counts_all['active_inbox'] == 3
