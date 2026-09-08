"""All Mail scope + progressive backfill regression tests.

Mailbox model:
  ACTIVE INBOX  — messages carrying Gmail INBOX
  ALL MAIL      — active inbox + archived (never spam/trash/draft/sent-only)
  EXCLUDED      — spam, trash, draft, sent-only

Visibility (All Mail) and intelligence eligibility are SEPARATE concepts:
archived mail is visible in All Mail but never feeds briefing, attention,
needs-reply, tasks, deadlines, or the analysis queue.
"""
import json
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

import pytest

from backend.app.db.repositories import Repository
from backend.app.schemas import Email, EmailAccount
from backend.app.mail.eligibility import MailEligibilityPolicy
from backend.app.mail.providers.gmail import GmailProvider


def _email(eid, labels, sender="a@b.com"):
    scoped_id = f"gmail_gmail_user_{eid}"
    return Email(id=scoped_id, account_id="gmail_user", sender=sender, subject=f"subject {eid}",
                 body="body", label_ids=labels)


@pytest.fixture
def repo(tmp_path):
    r = Repository(tmp_path / "allmail.db")
    yield r
    r.con.close()


# ═══════════════════════════════════════════════════════════════════
# SCOPES
# ═══════════════════════════════════════════════════════════════════

def test_inbox_scope_shows_active_inbox_only(repo):
    repo.upsert_email(_email("in1", ["INBOX", "UNREAD"]), "1")
    repo.upsert_email(_email("arch1", ["UNREAD"]), "2")
    repo.upsert_email(_email("spam1", ["SPAM"]), "3")
    assert [e.id for e in repo.emails_filtered(scope="inbox")] == ["gmail_gmail_user_in1"]


def test_all_scope_includes_archived(repo):
    repo.upsert_email(_email("in1", ["INBOX", "UNREAD"]), "1")
    repo.upsert_email(_email("arch1", ["UNREAD"]), "2")
    repo.upsert_email(_email("arch2", ["CATEGORY_PROMOTIONS"]), "3")
    ids = {e.id for e in repo.emails_filtered(scope="all")}
    assert ids == {"gmail_gmail_user_in1", "gmail_gmail_user_arch1", "gmail_gmail_user_arch2"}


def test_all_scope_excludes_spam_trash_draft_only(repo):
    # All Mail = received inbox + archived received + SENT.
    # Spam, Trash, and Draft are never shown.
    repo.upsert_email(_email("in1", ["INBOX"]), "1")
    repo.upsert_email(_email("arch1", ["UNREAD"]), "2")
    repo.upsert_email(_email("sent1", ["SENT"]), "6")
    repo.upsert_email(_email("spam1", ["SPAM"]), "3")
    repo.upsert_email(_email("trash1", ["TRASH"]), "4")
    repo.upsert_email(_email("draft1", ["DRAFT"]), "5")
    ids = {e.id for e in repo.emails_filtered(scope="all")}
    assert ids == {"gmail_gmail_user_in1", "gmail_gmail_user_arch1", "gmail_gmail_user_sent1"}


def test_all_scope_kind_filters(repo):
    repo.upsert_email(_email("in1", ["INBOX"]), "1")
    repo.upsert_email(_email("arch1", ["UNREAD"]), "2")
    repo.upsert_email(_email("sent1", ["SENT"]), "3")
    assert {e.id for e in repo.emails_filtered(scope="all", kind="received")} == {"gmail_gmail_user_in1", "gmail_gmail_user_arch1"}
    assert {e.id for e in repo.emails_filtered(scope="all", kind="sent")} == {"gmail_gmail_user_sent1"}
    assert {e.id for e in repo.emails_filtered(scope="all", kind="archived")} == {"gmail_gmail_user_arch1"}


def test_sent_visible_but_excluded_from_intelligence(repo):
    repo.upsert_email(_email("sent1", ["SENT"]), "1")
    # visible in All Mail
    assert {e.id for e in repo.emails_filtered(scope="all")} == {"gmail_gmail_user_sent1"}
    # never in inbox scope
    assert repo.emails_filtered(scope="inbox") == []
    # sent never feeds the pipeline
    from backend.app.mail.eligibility import MailEligibilityPolicy
    assert MailEligibilityPolicy.should_include_in_briefing(["SENT"]) is False
    assert MailEligibilityPolicy.should_schedule_analysis(["SENT"]) is False
    assert MailEligibilityPolicy.pipeline_eligibility(["SENT"]).value == "excluded"
    # and never enters the analysis queue
    assert repo.eligible_emails_without_analysis("qwen3:4b") == []


def test_draft_excluded_from_all_mail_and_search(repo):
    repo.upsert_email(_email("draft1", ["DRAFT"], sender="drafter@x.com"), "1")
    repo.upsert_email(_email("in1", ["INBOX"]), "2")
    assert {e.id for e in repo.emails_filtered(scope="all")} == {"gmail_gmail_user_in1"}
    assert {e.id for e in repo.search_emails("drafter")} == set()


def test_category_ignored_in_all_scope(repo):
    # Gmail tab semantics belong to the Inbox experience — an archived
    # Promotions message must not vanish from All Mail.
    repo.upsert_email(_email("inpromo", ["INBOX", "CATEGORY_PROMOTIONS"]), "1")
    repo.upsert_email(_email("archpromo", ["CATEGORY_PROMOTIONS"]), "2")
    ids = {e.id for e in repo.emails_filtered(scope="all", category="promotions")}
    assert ids == {"gmail_gmail_user_inpromo", "gmail_gmail_user_archpromo"}
    # Inbox scope still applies the tab
    ids_inbox = {e.id for e in repo.emails_filtered(scope="inbox", category="promotions")}
    assert ids_inbox == {"gmail_gmail_user_inpromo"}


def test_search_covers_archived_not_spam(repo):
    repo.upsert_email(_email("arch1", ["UNREAD"], sender="archived@x.com"), "1")
    repo.upsert_email(_email("spam1", ["SPAM"], sender="spammer@x.com"), "2")
    hits = {e.id for e in repo.search_emails("archived")}
    assert hits == {"gmail_gmail_user_arch1"}
    hits2 = {e.id for e in repo.search_emails("spammer")}
    assert hits2 == set()


def test_counts_report_inbox_allmail_excluded(repo):
    repo.upsert_email(_email("in1", ["INBOX", "CATEGORY_PERSONAL"]), "1")
    repo.upsert_email(_email("arch1", ["UNREAD"]), "2")
    repo.upsert_email(_email("spam1", ["SPAM"]), "3")
    counts = repo.email_counts()
    assert counts["active_inbox"] == 1
    assert counts["all_mail"] == 2
    assert counts["excluded"] == 1
    assert counts["categories"]["primary"] == 1


def test_pagination_in_all_scope(repo):
    for i in range(7):
        repo.upsert_email(_email(f"m{i}", ["UNREAD"]), str(i))
    page1 = repo.emails_filtered(scope="all", limit=5, offset=0)
    page2 = repo.emails_filtered(scope="all", limit=5, offset=5)
    assert len(page1) == 5
    assert len(page2) == 2
    ids1 = {e.id for e in page1}
    ids2 = {e.id for e in page2}
    assert not ids1 & ids2


# ═══════════════════════════════════════════════════════════════════
# ARCHIVED VS INTELLIGENCE (pipeline stays inbox-only)
# ═══════════════════════════════════════════════════════════════════

def test_archived_excluded_from_intelligence(repo):
    repo.upsert_email(_email("arch1", ["UNREAD"]), "1")
    repo.upsert_email(_email("in1", ["INBOX"]), "2")

    # visible in All Mail
    assert {e.id for e in repo.emails_filtered(scope="all")} == {"gmail_gmail_user_arch1", "gmail_gmail_user_in1"}
    # but not in inbox scope
    assert [e.id for e in repo.emails_filtered(scope="inbox")] == ["gmail_gmail_user_in1"]
    # and never briefing-eligible
    assert MailEligibilityPolicy.should_include_in_briefing(["UNREAD"]) is False
    # and never scheduled for analysis
    assert MailEligibilityPolicy.should_schedule_analysis(["UNREAD"]) is False
    # analysis queue candidates remain inbox-only
    candidates = repo.eligible_emails_without_analysis("qwen3:4b")
    assert {e.id for e in candidates} == {"gmail_gmail_user_in1"}


def test_archived_tasks_not_in_active_projection(repo):
    from backend.app.schemas import Task
    repo.upsert_email(_email("arch1", ["UNREAD"]), "1")
    repo.upsert_email(_email("in1", ["INBOX"]), "2")
    repo.save_tasks_batch([
        Task(id="t_arch", source_email_id="gmail_gmail_user_arch1", title="old task", status="pending"),
        Task(id="t_in", source_email_id="gmail_gmail_user_in1", title="current task", status="pending"),
    ])
    active_ids = {t.id for t in repo.active_tasks()}
    assert active_ids == {"t_in"}
    # historical row preserved
    assert {t.id for t in repo.tasks()} == {"t_arch", "t_in"}


# ═══════════════════════════════════════════════════════════════════
# PROGRESSIVE BACKFILL (provider)
# ═══════════════════════════════════════════════════════════════════

def _base64(text: str) -> str:
    import base64
    return base64.urlsafe_b64encode(text.encode("utf-8")).decode("ascii")


def _detail(msg_id, subject, labels):
    return {
        "id": msg_id,
        "threadId": f"thread_{msg_id}",
        "internalDate": "1786000000000",
        "labelIds": labels,
        "snippet": f"snippet {subject}",
        "payload": {
            "headers": [
                {"name": "From", "value": f"Sender <s@{msg_id}.com>"},
                {"name": "To", "value": "user@gmail.com"},
                {"name": "Subject", "value": subject},
            ],
            "parts": [{"mimeType": "text/plain", "body": {"data": _base64("hello")}}],
        },
    }


def _account(repo, cursor=None):
    account = EmailAccount(
        id="gmail_user", provider="gmail", email_address="user@gmail.com",
        display_name="User", connection_status="connected", sync_cursor=cursor
    )
    repo.save_account(account)
    return account


@patch("httpx.AsyncClient.get")
def test_backfill_first_page_and_resume(mock_get, repo):
    provider = GmailProvider("cid", "secret")
    account = _account(repo)  # no cursor → backfill not started

    # Page 1: two messages, nextPageToken present
    list1 = MagicMock(); list1.status_code = 200
    list1.json.return_value = {
        "messages": [
            {"id": "arch_1", "threadId": "t1", "labelIds": ["UNREAD"]},
            {"id": "arch_2", "threadId": "t2", "labelIds": ["CATEGORY_PROMOTIONS"]},
        ],
        "nextPageToken": "page_2",
    }
    d1 = MagicMock(); d1.status_code = 200
    d1.json.return_value = _detail("arch_1", "Archived one", ["UNREAD"])
    d2 = MagicMock(); d2.status_code = 200
    d2.json.return_value = _detail("arch_2", "Archived two", ["CATEGORY_PROMOTIONS"])
    mock_get.side_effect = [list1, d1, d2]

    creds = {"access_token": "tok", "refresh_token": "ref",
             "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()}
    res = asyncio.run(provider.backfill_messages(account, creds, repo, page_size=50))
    assert res["imported"] == 2
    assert res["has_more"] is True

    # typed cursor persisted with the page token and counters
    cursor = json.loads(repo.account("gmail_user").sync_cursor)
    assert cursor["backfill_state"] == "running"
    assert cursor["backfill_page_token"] == "page_2"
    assert cursor["backfill_imported"] == 2
    assert cursor["backfill_pages"] == 1

    # Page 2 (resume after restart): one message, no nextPageToken
    list2 = MagicMock(); list2.status_code = 200
    list2.json.return_value = {
        "messages": [{"id": "arch_3", "threadId": "t3", "labelIds": ["UNREAD"]}],
    }
    d3 = MagicMock(); d3.status_code = 200
    d3.json.return_value = _detail("arch_3", "Archived three", ["UNREAD"])
    mock_get.side_effect = [list2, d3]

    account2 = repo.account("gmail_user")
    res2 = asyncio.run(provider.backfill_messages(account2, creds, repo, page_size=50))
    assert res2["imported"] == 1
    assert res2["has_more"] is False
    assert res2["complete"] is True

    cursor2 = json.loads(repo.account("gmail_user").sync_cursor)
    assert cursor2["backfill_state"] == "complete"
    assert cursor2["backfill_page_token"] is None
    assert cursor2["backfill_imported"] == 3
    assert cursor2["backfill_pages"] == 2

    # duplicates skipped (idempotent)
    res3 = asyncio.run(provider.backfill_messages(repo.account("gmail_user"), creds, repo))
    assert res3["imported"] == 0
    assert res3["complete"] is True

    # all three archived, none in active inbox
    assert repo.email("gmail_gmail_user_arch_1") is not None
    assert repo.email_counts()["active_inbox"] == 0
    assert repo.email_counts()["all_mail"] == 3


@patch("httpx.AsyncClient.get")
def test_backfill_skips_cached_rows_and_updates_labels(mock_get, repo):
    provider = GmailProvider("cid", "secret")
    repo.upsert_email(_email("cached_1", ["UNREAD"]), "h1")
    account = _account(repo, json.dumps({"history_id": "100", "next_page_token": None}))

    list1 = MagicMock(); list1.status_code = 200
    list1.json.return_value = {
        "messages": [{"id": "cached_1", "threadId": "t1", "labelIds": ["STARRED"]}],
    }
    mock_get.side_effect = [list1]

    creds = {"access_token": "tok", "refresh_token": "ref",
             "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()}
    res = asyncio.run(provider.backfill_messages(account, creds, repo))
    assert res["imported"] == 0
    assert res["skipped_duplicates"] == 1
    # label set refreshed without a body fetch
    assert repo.email_eligibility("gmail_gmail_user_cached_1")["label_ids"] == ["STARRED"]
    assert repo.email_counts()["all_mail"] == 1


@patch("httpx.AsyncClient.get")
def test_backfill_never_requests_spam_trash(mock_get, repo):
    provider = GmailProvider("cid", "secret")
    account = _account(repo)

    list1 = MagicMock(); list1.status_code = 200
    list1.json.return_value = {"messages": []}
    mock_get.side_effect = [list1]

    creds = {"access_token": "tok", "refresh_token": "ref",
             "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()}
    asyncio.run(provider.backfill_messages(account, creds, repo))

    call = mock_get.call_args
    params = call[1]["params"]
    assert params["includeSpamTrash"] == "false"
    assert params["q"] == "-label:INBOX"
    assert "pageToken" not in params
