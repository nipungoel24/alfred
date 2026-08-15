import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
from backend.app.schemas import EmailAccount, Email, EmailAnalysis, Priority, Category, Deadline, ActionItem
from backend.app.mail.providers.gmail import GmailProvider
from backend.app.db.repositories import Repository
from backend.app.db.secure_store import encrypt_token, decrypt_token

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

# 3. Synchronize Mailbox & Normalization & Task Extraction Mock
@patch("httpx.AsyncClient.get")
def test_gmail_sync_flow(mock_get, mock_gmail, temp_repo):
    # Set up mock endpoints
    list_response = MagicMock()
    list_response.status_code = 200
    list_response.json.return_value = {
        "messages": [{"id": "gmail_msg_100", "threadId": "gmail_thread_200"}]
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
                {"name": "Subject", "value": "Renewal failed - action required"}
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

    # Side effect: first list, then detail
    mock_get.side_effect = [list_response, detail_response]

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
    assert "Please update your payment card" in email.body

    # Now verify Task Extraction: Save analysis for this email
    analysis = EmailAnalysis(
        short_summary="SaaS invoice failed",
        category=Category.finance,
        priority=Priority.urgent,
        priority_score=90,
        reason_for_priority="Critical billing issue",
        needs_reply=True,
        action_items=[ActionItem(description="Update card", owner="User", deadline="5 PM today")],
        deadlines=[Deadline(description="Pay invoice", due_at="before 5 PM today", confidence="explicit")]
    )
    temp_repo.save_analysis("gmail_msg_100", "fingerprint_abc", "qwen3:4b", analysis)

    # Check tasks extracted automatically!
    tasks_list = temp_repo.tasks()
    assert len(tasks_list) == 2
    
    # Assert specific task fields
    action_task = next(t for t in tasks_list if t.id == "task_gmail_msg_100_0")
    assert action_task.title == "Update card"
    assert action_task.due_at == "5 PM today"
    assert action_task.priority == "urgent"
    assert action_task.source_email_id == "gmail_msg_100"

    deadline_task = next(t for t in tasks_list if t.id == "deadline_gmail_msg_100_0")
    assert deadline_task.title == "Pay invoice"
    assert deadline_task.due_at == "before 5 PM today"
    assert deadline_task.priority == "urgent"

def base64_encode_string(text: str) -> str:
    return base64_url_encode(text.encode("utf-8"))

def base64_url_encode(data: bytes) -> str:
    import base64
    return base64.urlsafe_b64encode(data).decode("ascii")
