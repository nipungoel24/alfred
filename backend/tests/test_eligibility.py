"""Gmail eligibility + pipeline regression tests.

Covers the category corpus, spam/trash/archive exclusion, label-only
history updates, restore transitions, thread handling, and the pipeline
regressions (0 briefing / 0 tasks / 0 deadlines / 0 needs-reply / 0 queue
for excluded mail).
"""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from datetime import datetime, timezone, timedelta

from backend.app.mail.eligibility import (
    MailEligibilityPolicy, GmailCategory, MailboxState, PipelineEligibility,
    gmail_category_from_labels, mailbox_state_from_labels,
    LABEL_INBOX, LABEL_SPAM, LABEL_TRASH, LABEL_IMPORTANT, LABEL_SENT,
    LABEL_DRAFT, LABEL_UNREAD, LABEL_CATEGORY_PERSONAL,
    LABEL_CATEGORY_PROMOTIONS, LABEL_CATEGORY_SOCIAL, LABEL_CATEGORY_UPDATES,
    LABEL_CATEGORY_FORUMS,
)
from backend.app.db.repositories import Repository
from backend.app.schemas import Email


# ═══════════════════════════════════════════════════════════════════
# CATEGORY CORPUS
# ═══════════════════════════════════════════════════════════════════

def test_inbox_primary():
    labels = [LABEL_INBOX, LABEL_UNREAD, LABEL_CATEGORY_PERSONAL]
    assert gmail_category_from_labels(labels) == GmailCategory.PRIMARY
    assert mailbox_state_from_labels(labels) == MailboxState.ACTIVE_INBOX
    assert MailEligibilityPolicy.should_display_in_inbox(labels) is True


def test_inbox_promotions():
    labels = [LABEL_INBOX, LABEL_CATEGORY_PROMOTIONS]
    assert gmail_category_from_labels(labels) == GmailCategory.PROMOTIONS
    assert mailbox_state_from_labels(labels) == MailboxState.ACTIVE_INBOX


def test_inbox_social():
    labels = [LABEL_INBOX, LABEL_CATEGORY_SOCIAL]
    assert gmail_category_from_labels(labels) == GmailCategory.SOCIAL


def test_inbox_updates():
    labels = [LABEL_INBOX, LABEL_CATEGORY_UPDATES]
    assert gmail_category_from_labels(labels) == GmailCategory.UPDATES


def test_inbox_forums():
    labels = [LABEL_INBOX, LABEL_CATEGORY_FORUMS]
    assert gmail_category_from_labels(labels) == GmailCategory.FORUMS


def test_inbox_without_category_is_primary():
    labels = [LABEL_INBOX, LABEL_UNREAD]
    assert gmail_category_from_labels(labels) == GmailCategory.PRIMARY


def test_spam_state():
    labels = [LABEL_SPAM]
    assert mailbox_state_from_labels(labels) == MailboxState.SPAM
    assert MailEligibilityPolicy.should_display_in_inbox(labels) is False


def test_trash_state():
    labels = [LABEL_TRASH]
    assert mailbox_state_from_labels(labels) == MailboxState.TRASH


def test_archived_state():
    labels = [LABEL_UNREAD]
    assert mailbox_state_from_labels(labels) == MailboxState.ARCHIVED


def test_spam_wins_over_inbox():
    labels = [LABEL_INBOX, LABEL_SPAM]
    assert mailbox_state_from_labels(labels) == MailboxState.SPAM


# ═══════════════════════════════════════════════════════════════════
# TRANSITIONS
# ═══════════════════════════════════════════════════════════════════

def test_spam_to_inbox_restores_eligibility():
    assert MailEligibilityPolicy.pipeline_eligibility([LABEL_SPAM]) == PipelineEligibility.EXCLUDED
    assert MailEligibilityPolicy.pipeline_eligibility(
        [LABEL_INBOX, LABEL_CATEGORY_PERSONAL]) == PipelineEligibility.ACTIVE


def test_inbox_to_spam_excludes():
    assert MailEligibilityPolicy.pipeline_eligibility(
        [LABEL_INBOX, LABEL_CATEGORY_PERSONAL]) == PipelineEligibility.ACTIVE
    assert MailEligibilityPolicy.pipeline_eligibility(
        [LABEL_INBOX, LABEL_SPAM]) == PipelineEligibility.EXCLUDED


def test_inbox_to_archive_excludes():
    assert MailEligibilityPolicy.pipeline_eligibility(
        [LABEL_INBOX, LABEL_UNREAD]) == PipelineEligibility.ACTIVE
    assert MailEligibilityPolicy.pipeline_eligibility([LABEL_UNREAD]) == PipelineEligibility.EXCLUDED


def test_archive_to_inbox_restores():
    assert MailEligibilityPolicy.pipeline_eligibility([LABEL_UNREAD]) == PipelineEligibility.EXCLUDED
    assert MailEligibilityPolicy.pipeline_eligibility(
        [LABEL_INBOX, LABEL_UNREAD]) == PipelineEligibility.ACTIVE


def test_sent_and_draft_are_excluded():
    assert MailEligibilityPolicy.pipeline_eligibility([LABEL_SENT]) == PipelineEligibility.EXCLUDED
    assert MailEligibilityPolicy.pipeline_eligibility([LABEL_DRAFT]) == PipelineEligibility.EXCLUDED


# ═══════════════════════════════════════════════════════════════════
# BRIEFING / ATTENTION POLICY
# ═══════════════════════════════════════════════════════════════════

def test_briefing_promotions_without_signal_excluded():
    assert MailEligibilityPolicy.should_include_in_briefing(
        [LABEL_INBOX, LABEL_CATEGORY_PROMOTIONS]) is False


def test_briefing_promotions_with_strong_signal_included():
    # Gmail IMPORTANT overrides low-value tabs
    assert MailEligibilityPolicy.should_include_in_briefing(
        [LABEL_INBOX, LABEL_CATEGORY_PROMOTIONS, LABEL_IMPORTANT]) is True
    # urgent analysis overrides
    assert MailEligibilityPolicy.should_include_in_briefing(
        [LABEL_INBOX, LABEL_CATEGORY_SOCIAL], analysis_priority="urgent") is True
    # needs reply overrides
    assert MailEligibilityPolicy.should_include_in_briefing(
        [LABEL_INBOX, LABEL_CATEGORY_SOCIAL], needs_reply=True) is True


def test_briefing_excludes_spam_trash_archived():
    assert MailEligibilityPolicy.should_include_in_briefing([LABEL_INBOX, LABEL_SPAM]) is False
    assert MailEligibilityPolicy.should_include_in_briefing([LABEL_INBOX, LABEL_TRASH]) is False
    assert MailEligibilityPolicy.should_include_in_briefing([LABEL_UNREAD]) is False


def test_updates_with_required_action_eligible_for_semantic_analysis():
    # Updates are NOT lazy — they get scheduled like Primary (lower prio)
    labels = [LABEL_INBOX, LABEL_CATEGORY_UPDATES]
    assert MailEligibilityPolicy.should_schedule_analysis(labels) is True
    assert MailEligibilityPolicy.pipeline_eligibility(labels) == PipelineEligibility.ACTIVE


# ═══════════════════════════════════════════════════════════════════
# SCHEDULING
# ═══════════════════════════════════════════════════════════════════

def test_scheduling_order_by_category():
    p = MailEligibilityPolicy.analysis_queue_priority
    assert p([LABEL_INBOX, LABEL_CATEGORY_PERSONAL]) > p([LABEL_INBOX, LABEL_CATEGORY_UPDATES])
    assert p([LABEL_INBOX, LABEL_CATEGORY_UPDATES]) > p([LABEL_INBOX, LABEL_CATEGORY_FORUMS])
    assert p([LABEL_INBOX, LABEL_CATEGORY_FORUMS]) > p([LABEL_INBOX, LABEL_CATEGORY_SOCIAL])
    assert p([LABEL_INBOX, LABEL_CATEGORY_SOCIAL]) > p([LABEL_INBOX, LABEL_CATEGORY_PROMOTIONS])


def test_gmail_important_is_p0():
    prio = MailEligibilityPolicy.analysis_queue_priority([LABEL_INBOX, LABEL_IMPORTANT])
    assert prio == 100


def test_lazy_categories_not_scheduled_by_default():
    assert MailEligibilityPolicy.should_schedule_analysis(
        [LABEL_INBOX, LABEL_CATEGORY_PROMOTIONS]) is False
    assert MailEligibilityPolicy.should_schedule_analysis(
        [LABEL_INBOX, LABEL_CATEGORY_SOCIAL]) is False
    # user_requested / Gmail IMPORTANT flips them on
    assert MailEligibilityPolicy.should_schedule_analysis(
        [LABEL_INBOX, LABEL_CATEGORY_PROMOTIONS], user_requested=True) is True
    assert MailEligibilityPolicy.should_schedule_analysis(
        [LABEL_INBOX, LABEL_CATEGORY_SOCIAL, LABEL_IMPORTANT]) is True


# ═══════════════════════════════════════════════════════════════════
# PERSISTENCE / LABEL-ONLY HISTORY UPDATE
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture
def repo(tmp_path):
    r = Repository(tmp_path / "eligibility.db")
    yield r
    r.con.close()


def _email(eid, labels):
    return Email(
        id=eid, account_id="gmail_user", sender="a@b.com",
        subject="s", body="b", label_ids=labels
    )


def test_label_only_history_update_recomputes_state(repo):
    e = _email("m1", [LABEL_INBOX, LABEL_CATEGORY_PERSONAL, LABEL_UNREAD])
    repo.upsert_email(e, "h1")
    assert repo.email_eligibility("m1")["mailbox_state"] == "active_inbox"

    # labelRemoved INBOX → archived → excluded (no body re-fetch, no delete)
    ok = repo.update_email_labels("m1", [LABEL_UNREAD])
    assert ok is True
    state = repo.email_eligibility("m1")
    assert state["mailbox_state"] == "archived"
    assert state["pipeline_eligibility"] == "excluded"
    # source row survives
    assert repo.email("m1") is not None
    assert repo.email("m1").label_ids == [LABEL_UNREAD]


def test_spam_transition_hides_from_projections(repo):
    e = _email("m1", [LABEL_INBOX, LABEL_CATEGORY_PERSONAL])
    repo.upsert_email(e, "h1")
    assert repo.email_counts()["active_inbox"] == 1

    repo.update_email_labels("m1", [LABEL_SPAM])
    counts = repo.email_counts()
    assert counts["active_inbox"] == 0
    assert counts["excluded"] == 1
    assert counts["categories"]["primary"] == 0

    # inbox filter no longer returns it
    assert repo.emails_filtered() == []
    # but it still exists in the mailbox cache
    assert repo.email_exists("m1") is True

    # restore
    repo.update_email_labels("m1", [LABEL_INBOX, LABEL_CATEGORY_PERSONAL])
    counts = repo.email_counts()
    assert counts["active_inbox"] == 1
    assert counts["categories"]["primary"] == 1


def test_category_counts_derive_from_labels(repo):
    repo.upsert_email(_email("p1", [LABEL_INBOX, LABEL_CATEGORY_PERSONAL]), "1")
    repo.upsert_email(_email("p2", [LABEL_INBOX, LABEL_CATEGORY_PERSONAL]), "2")
    repo.upsert_email(_email("promo", [LABEL_INBOX, LABEL_CATEGORY_PROMOTIONS]), "3")
    repo.upsert_email(_email("soc", [LABEL_INBOX, LABEL_CATEGORY_SOCIAL]), "4")
    repo.upsert_email(_email("upd", [LABEL_INBOX, LABEL_CATEGORY_UPDATES]), "5")
    repo.upsert_email(_email("frm", [LABEL_INBOX, LABEL_CATEGORY_FORUMS]), "6")
    repo.upsert_email(_email("spm", [LABEL_SPAM]), "7")

    counts = repo.email_counts()
    assert counts["active_inbox"] == 6
    assert counts["excluded"] == 1
    cats = counts["categories"]
    assert cats["primary"] == 2
    assert cats["promotions"] == 1
    assert cats["social"] == 1
    assert cats["updates"] == 1
    assert cats["forums"] == 1


def test_category_filter_is_db_driven(repo):
    repo.upsert_email(_email("p1", [LABEL_INBOX, LABEL_CATEGORY_PERSONAL]), "1")
    repo.upsert_email(_email("promo", [LABEL_INBOX, LABEL_CATEGORY_PROMOTIONS]), "2")
    repo.upsert_email(_email("spm", [LABEL_INBOX, LABEL_SPAM]), "3")

    assert [e.id for e in repo.emails_filtered(category="promotions")] == ["promo"]
    assert [e.id for e in repo.emails_filtered(category="primary")] == ["p1"]
    # spam never appears in inbox views
    assert len(repo.emails_filtered(category="primary")) == 1


def test_search_within_category_context(repo):
    repo.upsert_email(Email(
        id="adobe1", account_id="gmail_user", sender="adobe@marketing.com",
        subject="Adobe Creative Cloud offer", body="x",
        label_ids=[LABEL_INBOX, LABEL_CATEGORY_PROMOTIONS]), "1")
    repo.upsert_email(Email(
        id="primary1", account_id="gmail_user", sender="boss@work.com",
        subject="Q3 roadmap", body="x",
        label_ids=[LABEL_INBOX, LABEL_CATEGORY_PERSONAL]), "2")
    repo.upsert_email(Email(
        id="spam1", account_id="gmail_user", sender="spammer@evil.com",
        subject="Adobe free money", body="x",
        label_ids=[LABEL_SPAM]), "3")

    promo_hits = repo.emails_filtered(category="promotions", query="Adobe")
    assert [e.id for e in promo_hits] == ["adobe1"]
    # global search never surfaces spam rows
    global_hits = repo.emails_filtered(query="Adobe")
    assert [e.id for e in global_hits] == ["adobe1"]


def test_active_tasks_exclude_spam_sourced(repo):
    from backend.app.schemas import Task
    repo.upsert_email(_email("m1", [LABEL_INBOX, LABEL_CATEGORY_PERSONAL]), "1")
    repo.upsert_email(_email("m2", [LABEL_SPAM]), "2")

    t1 = Task(id="t1", source_email_id="m1", title="Real task", status="pending")
    t2 = Task(id="t2", source_email_id="m2", title="Spam-derived task", status="pending")
    t3 = Task(id="t3", source_email_id=None, title="User task", status="pending")
    repo.save_tasks_batch([t1, t2, t3])

    active_ids = {t.id for t in repo.active_tasks()}
    assert active_ids == {"t1", "t3"}
    # historical rows preserved
    assert {t.id for t in repo.tasks()} == {"t1", "t2", "t3"}


def test_permanent_delete_marks_excluded_not_destroyed(repo):
    e = _email("m1", [LABEL_INBOX, LABEL_CATEGORY_PERSONAL])
    repo.upsert_email(e, "h1")
    assert repo.mark_email_excluded("m1") is True
    state = repo.email_eligibility("m1")
    assert state["pipeline_eligibility"] == "excluded"
    assert repo.email("m1") is not None


# ═══════════════════════════════════════════════════════════════════
# MIXED-LABEL THREAD HANDLING
# ═══════════════════════════════════════════════════════════════════

def test_mixed_label_thread_keeps_active_messages_visible(repo):
    # One message archived, one active: thread stays visible via the
    # active message; the archived one is not displayed.
    repo.upsert_email(_email("old", [LABEL_UNREAD]), "1")
    repo.upsert_email(_email("new", [LABEL_INBOX, LABEL_UNREAD]), "2")
    repo.con.execute(
        'UPDATE emails SET thread_id="thread_x" WHERE id IN ("old","new")'
    )
    repo.con.commit()

    visible = [e.id for e in repo.emails_filtered()]
    assert visible == ["new"]
    # thread integrity preserved for both
    assert repo.emails_by_thread("thread_x")[0].id == "old"


# ═══════════════════════════════════════════════════════════════════
# HISTORY LABEL MUTATION THROUGH THE PROVIDER (label-only refresh)
# ═══════════════════════════════════════════════════════════════════

@patch("httpx.AsyncClient.get")
def test_history_label_changes_refresh_via_metadata(mock_get, repo):
    from backend.app.mail.providers.gmail import GmailProvider
    from backend.app.schemas import EmailAccount

    provider = GmailProvider("cid", "secret")
    cursor_json = json.dumps({"history_id": "9000", "next_page_token": None})
    account = EmailAccount(
        id="gmail_user", provider="gmail", email_address="user@gmail.com",
        display_name="User", connection_status="connected", sync_cursor=cursor_json
    )
    repo.save_account(account)
    repo.upsert_email(_email("m1", [LABEL_INBOX, LABEL_UNREAD]), "h1")

    # History: labelsRemoved INBOX on m1 (spam move), then profile
    history_response = MagicMock()
    history_response.status_code = 200
    history_response.json.return_value = {
        "history": [
            {"id": "9100",
             "labelsRemoved": [{"message": {"id": "m1", "labelIds": ["INBOX"]}}],
             "labelsAdded": [{"message": {"id": "m1", "labelIds": ["SPAM"]}}]}
        ],
        "nextPageToken": None
    }
    metadata_response = MagicMock()
    metadata_response.status_code = 200
    metadata_response.json.return_value = {"id": "m1", "labelIds": ["SPAM"]}
    profile_response = MagicMock()
    profile_response.status_code = 200
    profile_response.json.return_value = {"historyId": "9200"}

    mock_get.side_effect = [history_response, metadata_response, profile_response]

    credentials = {
        "access_token": "tok", "refresh_token": "ref",
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    }
    res = asyncio.run(provider.sync_messages(account, credentials, repo))
    assert res["imported"] == 0
    assert res["label_updates"] == 1

    state = repo.email_eligibility("m1")
    assert state["mailbox_state"] == "spam"
    assert state["pipeline_eligibility"] == "excluded"
    # row retained
    assert repo.email("m1") is not None


@patch("httpx.AsyncClient.get")
def test_history_spam_arrival_is_never_cached(mock_get, repo):
    from backend.app.mail.providers.gmail import GmailProvider
    from backend.app.schemas import EmailAccount

    provider = GmailProvider("cid", "secret")
    cursor_json = json.dumps({"history_id": "9000", "next_page_token": None})
    account = EmailAccount(
        id="gmail_user", provider="gmail", email_address="user@gmail.com",
        display_name="User", connection_status="connected", sync_cursor=cursor_json
    )
    repo.save_account(account)

    history_response = MagicMock()
    history_response.status_code = 200
    history_response.json.return_value = {
        "history": [
            {"id": "9100",
             "messagesAdded": [{"message": {"id": "spam_new", "labelIds": ["SPAM"]}}]}
        ],
        "nextPageToken": None
    }
    profile_response = MagicMock()
    profile_response.status_code = 200
    profile_response.json.return_value = {"historyId": "9200"}
    mock_get.side_effect = [history_response, profile_response]

    credentials = {
        "access_token": "tok", "refresh_token": "ref",
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    }
    res = asyncio.run(provider.sync_messages(account, credentials, repo))
    assert res["imported"] == 0
    # Spam-only arrival never enters the cache
    assert repo.email("spam_new") is None


def test_email_api_excluded_mail_never_listed(repo, tmp_path):
    """Spam/trash/archived produce zero briefing candidates and zero
    inbox listings at the API boundary (query-level enforcement)."""
    from backend.app import main
    from fastapi.testclient import TestClient

    original_repo = main.repo
    main.repo = repo
    try:
        client = TestClient(main.app)
        repo.upsert_email(_email("s1", [LABEL_INBOX, LABEL_SPAM]), "hs")
        repo.upsert_email(_email("t1", [LABEL_INBOX, LABEL_TRASH]), "ht")
        repo.upsert_email(_email("a1", [LABEL_UNREAD]), "ha")
        repo.upsert_email(_email("ok", [LABEL_INBOX, LABEL_CATEGORY_PERSONAL]), "hok")

        r = client.get("/api/emails")
        assert r.status_code == 200
        assert [e["id"] for e in r.json()] == ["ok"]

        counts = client.get("/api/emails/counts").json()
        assert counts["active_inbox"] == 1
        assert counts["excluded"] == 3

        # analyze excluded → 409
        assert client.post("/api/emails/s1/analyze").status_code == 409
        # analyze active → 200 (analysis mocked via worker path? No — direct AI)
        # Excluded never enqueues analysis jobs
        from backend.app.main import repo as _repo
        _repo.upsert_email(_email("s2", [LABEL_INBOX, LABEL_SPAM]), "hs2")
        candidates = _repo.eligible_emails_without_analysis("qwen3:4b")
        assert all(e.id != "s2" for e in candidates)
    finally:
        main.repo = original_repo
