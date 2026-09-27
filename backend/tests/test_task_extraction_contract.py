"""Regression tests for the task-extraction contract.

Every case here corresponds to malformed data that was found in the real
mailbox: due fields holding field labels and prose, dates used as task
titles, and "No action required" becoming a task.

The contract under test:

* ``due_at`` is a normalised ISO-8601 instant, or ``None``. Never prose,
  never a field label, never a bare clock time.
* A task title states something to DO. A date, a time, or a leaked field
  label is not a title.
* Malformed model output is rejected, never turned into a task.
* Priority and source linkage survive the round trip.
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend.app.schemas import (
    ActionItem,
    Category,
    Deadline,
    Email,
    EmailAnalysis,
    Priority,
    Task,
)
from backend.app.services.due_dates import is_temporal_only, normalize_due_at
from backend.app.services.task_derivation import derive_tasks

RECEIVED = datetime(2026, 9, 7, 17, 39, 54, tzinfo=timezone.utc)


def make_email(**kwargs) -> Email:
    base = dict(
        id="email-1",
        thread_id="thread-1",
        sender="sender@example.com",
        subject="Test",
        body="Test",
        received_at=RECEIVED,
    )
    base.update(kwargs)
    return Email(**base)


def make_analysis(*, action_items=(), deadlines=(), priority=Priority.high,
                  needs_reply=True) -> EmailAnalysis:
    return EmailAnalysis(
        short_summary="Test",
        category=Category.work,
        priority=priority,
        priority_score=80,
        reason_for_priority="Test",
        needs_reply=needs_reply,
        action_items=list(action_items),
        deadlines=list(deadlines),
    )


# ── 1. A normal actionable email yields a correct title ──────────────

def test_actionable_email_produces_the_action_as_the_title():
    tasks = derive_tasks(make_email(), make_analysis(action_items=[
        ActionItem(description="Submit the signed NDA", owner="user"),
    ]))
    assert len(tasks) == 1
    assert tasks[0].title == "Submit the signed NDA"
    assert tasks[0].owner == "user"
    assert tasks[0].status == "pending"


# ── 2. A date in the email lands in due_at, never in the title ───────

def test_date_becomes_due_at_not_the_title():
    tasks = derive_tasks(make_email(), make_analysis(action_items=[
        ActionItem(description="Submit the form", owner="user",
                   deadline="2026-09-12T00:00:00+00:00"),
    ]))
    assert len(tasks) == 1
    assert tasks[0].title == "Submit the form"
    assert tasks[0].due_at == "2026-09-12T00:00:00+00:00"
    assert "2026" not in tasks[0].title


# ── 3./4. Wording and leaked field labels never become due_at ─────────

@pytest.mark.parametrize("raw", [
    "due_at: soon",
    "due_at: join channel at earliest",
    "due_at",
    "due_at: 'Please Enable HTML'",
    "soon",
    "as soon as possible",
    "at the earliest",
    "next few days",
    "11:00 AM",
])
def test_unusable_deadline_becomes_null(raw):
    assert normalize_due_at(raw, reference=RECEIVED) is None

    tasks = derive_tasks(make_email(), make_analysis(action_items=[
        ActionItem(description="Join the channel", owner="user", deadline=raw),
    ]))
    # The task may still exist, but it never carries the junk as a due date.
    for task in tasks:
        assert task.due_at is None


# ── 5. An email with nothing actionable produces no task ─────────────

def test_no_action_required_creates_no_task():
    assert derive_tasks(make_email(), make_analysis(action_items=[
        ActionItem(description="No action required"),
    ])) == []


def test_receipt_creates_no_task():
    assert derive_tasks(make_email(), make_analysis(action_items=[
        ActionItem(description="Download your invoice", owner="user"),
    ])) == []


def test_pure_noise_creates_no_task():
    assert derive_tasks(make_email(), make_analysis(action_items=[
        ActionItem(description="Decode the base64 string", owner="user"),
    ])) == []


# ── 6. Malformed model output fails safely ───────────────────────────

@pytest.mark.parametrize("raw", [
    '{"short_summary":',
    "not json at all",
    '{"short_summary":"s"}',
    "[]",
])
def test_malformed_model_output_is_rejected(raw):
    with pytest.raises(ValidationError):
        EmailAnalysis.model_validate_json(raw)


def test_deadline_that_names_no_action_is_not_a_task():
    # The model emitted the date as the description. It describes no work.
    tasks = derive_tasks(make_email(), make_analysis(deadlines=[
        Deadline(description="12th September 2026", due_at="2026-09-12T00:00:00+00:00",
                 confidence="explicit"),
    ]))
    assert tasks == []


# ── 7. A missing due date is NULL, not a guess ───────────────────────

def test_missing_due_date_is_null():
    tasks = derive_tasks(make_email(), make_analysis(action_items=[
        ActionItem(description="Reply to the recruiter", owner="user"),
    ]))
    assert len(tasks) == 1
    assert tasks[0].due_at is None


# ── 8. Relative deadlines resolve only with a reference ──────────────

def test_relative_deadline_resolves_against_the_message_timestamp():
    tasks = derive_tasks(make_email(), make_analysis(action_items=[
        ActionItem(description="Confirm attendance", owner="user",
                   deadline="in 2 days"),
    ]))
    assert len(tasks) == 1
    assert tasks[0].due_at == "2026-09-09T17:39:54+00:00"


def test_relative_deadline_without_a_reference_stays_null():
    email = make_email(received_at=None)
    tasks = derive_tasks(email, make_analysis(action_items=[
        ActionItem(description="Confirm attendance", owner="user",
                   deadline="in 2 days"),
    ]))
    assert len(tasks) == 1
    assert tasks[0].due_at is None


def test_month_relative_deadline_is_refused_as_ambiguous():
    # "in 2 months" is not a fixed number of days; resolving it would be a guess.
    assert normalize_due_at("in 2 months", reference=RECEIVED) is None


# ── 9. An explicit priority is preserved ─────────────────────────────

def test_priority_is_taken_from_the_analysis():
    tasks = derive_tasks(
        make_email(),
        make_analysis(priority=Priority.urgent,
                      action_items=[ActionItem(description="Send the wire", owner="user")]),
    )
    assert tasks[0].priority == "urgent"


# ── 10. Source linkage survives derivation ───────────────────────────

def test_source_linkage_is_preserved():
    email = make_email(id="email-42", thread_id="thread-42")
    tasks = derive_tasks(email, make_analysis(action_items=[
        ActionItem(description="Send the wire", owner="user"),
    ]))
    assert tasks[0].source_email_id == "email-42"
    assert tasks[0].source_thread_id == "thread-42"


# ── Titles must describe an action ───────────────────────────────────

@pytest.mark.parametrize("bad_title", [
    "12th September 2026",
    "15 minutes from now",
    "due_at: soon",
    "due_at",
    "11:00 AM",
    "Sep 11th, 2026 (Friday)",
])
def test_non_action_titles_are_rejected(bad_title):
    assert is_temporal_only(bad_title) is True
    tasks = derive_tasks(make_email(), make_analysis(deadlines=[
        Deadline(description=bad_title, due_at="2026-09-12T00:00:00+00:00",
                 confidence="explicit"),
    ]))
    assert tasks == []


@pytest.mark.parametrize("good_title", [
    "Submit the signed NDA",
    "Reply to the recruiter",
    "Attend the campus drive",
])
def test_real_action_titles_are_kept(good_title):
    assert is_temporal_only(good_title) is False
    tasks = derive_tasks(make_email(), make_analysis(deadlines=[
        Deadline(description=good_title, due_at="2026-09-12T00:00:00+00:00",
                 confidence="explicit"),
    ]))
    assert len(tasks) == 1
    assert tasks[0].title == good_title


# ── owner is a field, not a line inside description ──────────────────

def test_owner_is_not_encoded_into_description():
    tasks = derive_tasks(make_email(), make_analysis(action_items=[
        ActionItem(description="Send the wire", owner="user"),
    ]))
    assert tasks[0].owner == "user"
    assert tasks[0].description is None
    assert "Owner:" not in (tasks[0].description or "")


# ── due_at always has one shape ─────────────────────────────────────

@pytest.mark.parametrize("raw,expected", [
    ("2026-09-12", "2026-09-12T00:00:00+00:00"),
    ("12th September 2026", "2026-09-12T00:00:00+00:00"),
    ("Sep 11th, 2026", "2026-09-11T00:00:00+00:00"),
    ("2026-09-12T17:00:00+00:00", "2026-09-12T17:00:00+00:00"),
])
def test_calendar_dates_normalise_to_one_iso_shape(raw, expected):
    assert normalize_due_at(raw, reference=RECEIVED) == expected


def test_task_due_at_is_never_prose():
    # The extraction boundary is what guarantees this. A stored task's due_at
    # is therefore either an ISO instant or absent, never a phrase.
    for raw in ("due_at: soon", "soon", "at the earliest", "next few days"):
        assert normalize_due_at(raw, reference=RECEIVED) is None

    tasks = derive_tasks(make_email(), make_analysis(action_items=[
        ActionItem(description="Do the thing", owner="user", deadline="due_at: soon"),
    ]))
    for task in tasks:
        assert task.due_at is None
        assert task.status in ("pending", "completed", "dismissed")


def test_a_resolvable_relative_offset_is_kept_as_an_instant():
    # "15 minutes from now" names no calendar date, but against the message
    # timestamp it is unambiguous, so it becomes a real instant rather than
    # being discarded.
    assert normalize_due_at("15 minutes from now", reference=RECEIVED) == "2026-09-07T17:54:54+00:00"


def test_relative_form_survives_the_schema_but_resolves_in_derivation():
    # The schema has no message timestamp, so it keeps a recognised relative
    # offset rather than discarding a form that is resolvable downstream.
    analysis = make_analysis(action_items=[
        ActionItem(description="Confirm attendance", owner="user", deadline="in 2 days"),
    ])
    assert analysis.action_items[0].deadline == "in 2 days"
    tasks = derive_tasks(make_email(), analysis)
    assert tasks[0].due_at == "2026-09-09T17:39:54+00:00"
