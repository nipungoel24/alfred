import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
from backend.app.schemas import EmailAccount, Email, EmailAnalysis, Priority, Category, Deadline, ActionItem
from backend.app.mail.providers.gmail import GmailProvider
from backend.app.db.repositories import Repository
from backend.app.db.secure_store import encrypt_token, decrypt_token
import httpx

@pytest.fixture
def mock_gmail():
    return GmailProvider(client_id="test_client_id", client_secret="test_client_secret")

@pytest.fixture
def temp_repo(tmp_path):
    db_file = tmp_path / "test_gmail.db"
    repo = Repository(db_file)
    yield repo
    repo.con.close()

# 1. OAuth URL Generation
def test_gmail_oauth_url_generation(mock_gmail):
    url = asyncio.run(mock_gmail.get_auth_url("http://localhost/callback", "test_state", "test_challenge"))
    assert "test_client_id" in url
    assert "http://localhost/callback" in url
    assert "gmail.readonly" in url
    assert "userinfo.email" in url
    assert "test_state" in url
    assert "test_challenge" in url

# 2. Token Exchange Mock
@patch("httpx.AsyncClient.post")
def test_gmail_token_exchange(mock_post, mock_gmail):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "mock_access",
        "refresh_token": "mock_refresh",
        "expires_in": 3600
    }
    mock_post.return_value = mock_response

    res = asyncio.run(mock_gmail.exchange_code("auth_code_123", "http://localhost/callback", "mock_verifier"))
    assert res["access_token"] == "mock_access"
    assert res["refresh_token"] == "mock_refresh"
    assert res["expires_in"] == 3600

# Helper to base64 encode strings
def base64_encode_string(text: str) -> str:
    import base64
    return base64.urlsafe_b64encode(text.encode("utf-8")).decode("ascii")

# 3. Initial Synchronize Mailbox (Full Sync) & Normalized Properties
@patch("httpx.AsyncClient.get")
def test_gmail_sync_initial(mock_get, mock_gmail, temp_repo):
    # Mock endpoints: 1. Profile, 2. Messages List, 3. Message Detail
    profile_response = MagicMock()
    profile_response.status_code = 200
    profile_response.json.return_value = {"historyId": "9999"}

    list_response = MagicMock()
    list_response.status_code = 200
    list_response.json.return_value = {
        "messages": [{"id": "gmail_msg_100", "threadId": "gmail_thread_200"}],
        "nextPageToken": "page_token_xyz"
    }

    detail_response = MagicMock()
    detail_response.status_code = 200
    detail_response.json.return_value = {
        "id": "gmail_msg_100",
        "threadId": "gmail_thread_200",
        "internalDate": "1786786974000",
        "payload": {
            "headers": [
                {"name": "From", "value": "Billing Department <billing@saas.com>"},
                {"name": "To", "value": "user@gmail.com"},
                {"name": "Subject", "value": "Renewal failed"}
            ],
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {
                        "data": base64_encode_string("Please update your payment card before 5 PM today.")
                    }
                }
            ]
        }
    }

    mock_get.side_effect = [profile_response, list_response, detail_response]

    # Save mock account in repository
    account = EmailAccount(
        id="gmail_user",
        provider="gmail",
        email_address="user@gmail.com",
        display_name="User",
        connection_status="connected"
    )
    temp_repo.save_account(account)

    credentials = {
        "access_token": "access_token_123",
        "refresh_token": "refresh_token_123",
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    }

    res = asyncio.run(mock_gmail.sync_messages(account, credentials, temp_repo))
    assert res["imported"] == 1

    # Verify normalization saved email details
    email = temp_repo.email("gmail_msg_100")
    assert email is not None
    assert email.sender == "billing@saas.com"
    assert email.sender_name == "Billing Department"
    assert email.thread_id == "gmail_thread_200"

    # Check sync_cursor contents
    updated_account = temp_repo.account("gmail_user")
    assert updated_account.sync_cursor is not None
    cursor = json.loads(updated_account.sync_cursor)
    assert cursor["history_id"] == "9999"
    assert cursor["next_page_token"] == "page_token_xyz"

# 4. Incremental Sync (using history API), label mutations, and non-destructive deletion
@patch("httpx.AsyncClient.get")
def test_gmail_sync_incremental(mock_get, mock_gmail, temp_repo):
    # Start with an already synced account
    cursor_json = json.dumps({"history_id": "9999", "next_page_token": "page_token_xyz"})
    account = EmailAccount(
        id="gmail_user",
        provider="gmail",
        email_address="user@gmail.com",
        display_name="User",
        connection_status="connected",
        sync_cursor=cursor_json
    )
    temp_repo.save_account(account)

    # Pre-populate repository with msg_100
    existing_email = Email(
        id="gmail_msg_100",
        thread_id="gmail_thread_200",
        account_id="gmail_user",
        sender="billing@saas.com",
        subject="Renewal failed",
        body="Please update your card",
        label_ids=["INBOX", "UNREAD", "CATEGORY_PERSONAL"]
    )
    temp_repo.upsert_email(existing_email, "hash_100")

    # Mocks: 1. History (adding msg_101, deleting msg_100), 2. Detail of msg_101, 3. Profile to fetch new historyId
    history_response = MagicMock()
    history_response.status_code = 200
    history_response.json.return_value = {
        "history": [
            {
                "id": "10000",
                "messagesAdded": [
                    {
                        "message": {"id": "gmail_msg_101", "threadId": "gmail_thread_200",
                                    "labelIds": ["INBOX", "UNREAD"]}
                    }
                ],
                "messagesDeleted": [
                    {
                        "message": {"id": "gmail_msg_100"}
                    }
                ]
            }
        ]
    }

    detail_response = MagicMock()
    detail_response.status_code = 200
    detail_response.json.return_value = {
        "id": "gmail_msg_101",
        "threadId": "gmail_thread_200",
        "internalDate": "1786786975000",
        "labelIds": ["INBOX", "UNREAD", "CATEGORY_PERSONAL"],
        "payload": {
            "headers": [
                {"name": "From", "value": "Billing Department <billing@saas.com>"},
                {"name": "To", "value": "user@gmail.com"},
                {"name": "Subject", "value": "Renewal succeeded"}
            ],
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {
                        "data": base64_encode_string("Thank you for updating your payment card.")
                    }
                }
            ]
        }
    }

    profile_response = MagicMock()
    profile_response.status_code = 200
    profile_response.json.return_value = {"historyId": "10005"}

    mock_get.side_effect = [history_response, detail_response, profile_response]

    credentials = {
        "access_token": "access_token_123",
        "refresh_token": "refresh_token_123",
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    }

    res = asyncio.run(mock_gmail.sync_messages(account, credentials, temp_repo))
    assert res["imported"] == 1

    # Verify msg_101 is imported
    assert temp_repo.email("gmail_msg_101") is not None
    # Verify msg_100 is NOT deleted: source row is retained for history
    # integrity and marked excluded instead.
    retained = temp_repo.email("gmail_msg_100")
    assert retained is not None

    from backend.app.db.database import connect
    con = temp_repo.con
    row = con.execute(
        'SELECT mailbox_state, pipeline_eligibility FROM emails WHERE id="gmail_msg_100"'
    ).fetchone()
    assert row["mailbox_state"] == "trash"
    assert row["pipeline_eligibility"] == "excluded"

    # Check updated cursor
    updated_account = temp_repo.account("gmail_user")
    cursor = json.loads(updated_account.sync_cursor)
    assert cursor["history_id"] == "10005"
    assert cursor["next_page_token"] == "page_token_xyz" # Next page token preserved for pagination!

# 5. History Expired (Recovery Sync via Full Sync)
@patch("httpx.AsyncClient.get")
def test_gmail_sync_history_expired_recovery(mock_get, mock_gmail, temp_repo):
    cursor_json = json.dumps({"history_id": "8888", "next_page_token": "page_token_xyz"})
    account = EmailAccount(
        id="gmail_user",
        provider="gmail",
        email_address="user@gmail.com",
        display_name="User",
        connection_status="connected",
        sync_cursor=cursor_json
    )
    temp_repo.save_account(account)

    # History API returns 410 Expired
    history_response = MagicMock()
    history_response.status_code = 410

    # Profile API
    profile_response = MagicMock()
    profile_response.status_code = 200
    profile_response.json.return_value = {"historyId": "10008"}

    # Messages list
    list_response = MagicMock()
    list_response.status_code = 200
    list_response.json.return_value = {
        "messages": [{"id": "gmail_msg_200", "threadId": "gmail_thread_300"}]
    }

    # Detail
    detail_response = MagicMock()
    detail_response.status_code = 200
    detail_response.json.return_value = {
        "id": "gmail_msg_200",
        "threadId": "gmail_thread_300",
        "internalDate": "1786786976000",
        "payload": {
            "headers": [
                {"name": "From", "value": "Newsletter <info@news.com>"},
                {"name": "To", "value": "user@gmail.com"},
                {"name": "Subject", "value": "Tech news"}
            ],
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {
                        "data": base64_encode_string("Weekly newsletter")
                    }
                }
            ]
        }
    }

    mock_get.side_effect = [history_response, profile_response, list_response, detail_response]

    credentials = {
        "access_token": "access_token_123",
        "refresh_token": "refresh_token_123",
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    }

    res = asyncio.run(mock_gmail.sync_messages(account, credentials, temp_repo))
    assert res["imported"] == 1
    assert temp_repo.email("gmail_msg_200") is not None

    # Check updated cursor has recovered historyId
    updated_account = temp_repo.account("gmail_user")
    cursor = json.loads(updated_account.sync_cursor)
    assert cursor["history_id"] == "10008"

# 6. Progressive Pagination (load_older = True)
@patch("httpx.AsyncClient.get")
def test_gmail_sync_load_older(mock_get, mock_gmail, temp_repo):
    cursor_json = json.dumps({"history_id": "10000", "next_page_token": "page_token_xyz"})
    account = EmailAccount(
        id="gmail_user",
        provider="gmail",
        email_address="user@gmail.com",
        display_name="User",
        connection_status="connected",
        sync_cursor=cursor_json
    )
    temp_repo.save_account(account)

    # Mocks: 1. Messages List (with pageToken), 2. Detail
    list_response = MagicMock()
    list_response.status_code = 200
    list_response.json.return_value = {
        "messages": [{"id": "gmail_msg_older_1", "threadId": "gmail_thread_999"}],
        "nextPageToken": "page_token_abc_older"
    }

    detail_response = MagicMock()
    detail_response.status_code = 200
    detail_response.json.return_value = {
        "id": "gmail_msg_older_1",
        "threadId": "gmail_thread_999",
        "internalDate": "1786786900000",
        "payload": {
            "headers": [
                {"name": "From", "value": "Old Friend <old@friend.com>"},
                {"name": "To", "value": "user@gmail.com"},
                {"name": "Subject", "value": "Long time no see"}
            ],
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {
                        "data": base64_encode_string("Hello, let's catch up.")
                    }
                }
            ]
        }
    }

    mock_get.side_effect = [list_response, detail_response]

    credentials = {
        "access_token": "access_token_123",
        "refresh_token": "refresh_token_123",
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    }

    res = asyncio.run(mock_gmail.sync_messages(account, credentials, temp_repo, load_older=True))
    assert res["imported"] == 1
    assert temp_repo.email("gmail_msg_older_1") is not None

    # Check updated sync cursor page token is advanced
    updated_account = temp_repo.account("gmail_user")
    cursor = json.loads(updated_account.sync_cursor)
    assert cursor["history_id"] == "10000" # History ID unchanged!
    assert cursor["next_page_token"] == "page_token_abc_older" # Advanced!

def test_gmail_html_sanitisation(mock_gmail):
    html_content = """
    <html>
        <head><style>body {color: red;}</style></head>
        <body>
            <h1>Hello World</h1>
            <p>This is a paragraph.</p>
            <script>alert('XSS');</script>
            <a href="javascript:alert('XSS')">Click here</a>
        </body>
    </html>
    """
    clean_body = mock_gmail._clean_html(html_content)
    # Assert scripts are stripped
    assert "alert('XSS')" not in clean_body
    # Assert styles are stripped
    assert "color: red" not in clean_body
    # Assert HTML tags are stripped
    assert "<html>" not in clean_body
    assert "<body>" not in clean_body
    # Assert text contents are preserved with layout newlines
    assert "Hello World" in clean_body
    assert "This is a paragraph." in clean_body
