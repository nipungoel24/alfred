"""Mailbox + pipeline eligibility policy for Alfred.

This module is the SINGLE authority for deciding how a Gmail message
participates in Alfred's intelligence pipeline. Rules here must never be
duplicated ad hoc in routes, the sync provider, or the analysis worker.

Concepts
--------
SOURCE EMAIL DATA != ACTIVE ALFRED ATTENTION DATA

A message can remain cached locally (for history reconciliation, thread
integrity, migration correctness) while being excluded from every current
attention projection: Briefing, Overview, Needs Reply, Tasks, Deadlines,
and the background AI queue.

Gmail is the source of truth for mailbox state. Alfred never invents a
second spam classifier; it consumes Gmail's label IDs as returned by the
API (labelAdded/labelRemoved history events keep them current).
"""
from __future__ import annotations

from enum import Enum

# ── Gmail system label IDs (stable, documented at
#    https://developers.google.com/gmail/api/guides/labels) ──
LABEL_INBOX = "INBOX"
LABEL_SPAM = "SPAM"
LABEL_TRASH = "TRASH"
LABEL_IMPORTANT = "IMPORTANT"
LABEL_STARRED = "STARRED"
LABEL_SENT = "SENT"
LABEL_DRAFT = "DRAFT"
LABEL_UNREAD = "UNREAD"

LABEL_CATEGORY_PERSONAL = "CATEGORY_PERSONAL"
LABEL_CATEGORY_SOCIAL = "CATEGORY_SOCIAL"
LABEL_CATEGORY_PROMOTIONS = "CATEGORY_PROMOTIONS"
LABEL_CATEGORY_UPDATES = "CATEGORY_UPDATES"
LABEL_CATEGORY_FORUMS = "CATEGORY_FORUMS"

SYSTEM_LABELS = {
    LABEL_INBOX, LABEL_SPAM, LABEL_TRASH, LABEL_IMPORTANT, LABEL_STARRED,
    LABEL_SENT, LABEL_DRAFT, LABEL_UNREAD,
    LABEL_CATEGORY_PERSONAL, LABEL_CATEGORY_SOCIAL, LABEL_CATEGORY_PROMOTIONS,
    LABEL_CATEGORY_UPDATES, LABEL_CATEGORY_FORUMS,
}


class MailboxState(str, Enum):
    """Where a message currently lives in Gmail, derived from its label IDs."""
    ACTIVE_INBOX = "active_inbox"   # has INBOX, not SPAM/TRASH/DRAFT/SENT
    ARCHIVED = "archived"           # no INBOX, no SPAM/TRASH, not SENT/DRAFT
    SPAM = "spam"
    TRASH = "trash"
    SENT = "sent"
    DRAFT = "draft"
    OTHER = "other"


class PipelineEligibility(str, Enum):
    """Whether a message should affect Alfred's current attention."""
    ACTIVE = "active"       # feeds briefing/attention/analysis queue
    DEFERRED = "deferred"   # analyzable later (promo/social), low priority
    EXCLUDED = "excluded"   # must not affect any current projection


class GmailCategory(str, Enum):
    """Gmail tab categories mapped onto Alfred's UI categories."""
    PRIMARY = "primary"
    PROMOTIONS = "promotions"
    SOCIAL = "social"
    UPDATES = "updates"
    FORUMS = "forums"


CATEGORY_LABEL_TO_UI = {
    LABEL_CATEGORY_PERSONAL: GmailCategory.PRIMARY,
    LABEL_CATEGORY_PROMOTIONS: GmailCategory.PROMOTIONS,
    LABEL_CATEGORY_SOCIAL: GmailCategory.SOCIAL,
    LABEL_CATEGORY_UPDATES: GmailCategory.UPDATES,
    LABEL_CATEGORY_FORUMS: GmailCategory.FORUMS,
}

# Low-value tabs are analyzed lazily (idle / on open / on demand).
LAZY_CATEGORIES = {GmailCategory.PROMOTIONS, GmailCategory.SOCIAL}


def gmail_category_from_labels(label_ids: list[str] | set[str] | None) -> GmailCategory:
    """Map Gmail CATEGORY_* labels onto the Alfred UI category.

    An active-Inbox message without any non-primary category label is
    treated as PRIMARY for UI purposes (CATEGORY_PERSONAL maps there too).
    Never uses an LLM — Gmail's classification is authoritative.
    """
    labels = set(label_ids or [])
    for gmail_label, ui_category in CATEGORY_LABEL_TO_UI.items():
        if gmail_label in labels:
            return ui_category
    return GmailCategory.PRIMARY


def mailbox_state_from_labels(label_ids: list[str] | set[str] | None) -> MailboxState:
    """Derive the explicit mailbox state from Gmail label IDs.

    Precedence order mirrors Gmail semantics: SPAM/TRASH win over INBOX,
    then DRAFT, then SENT, then INBOX. Anything else (no INBOX, none of
    the above — e.g. UNREAD-only after an inbox removal) is ARCHIVED.
    """
    labels = set(label_ids or [])
    if LABEL_SPAM in labels:
        return MailboxState.SPAM
    if LABEL_TRASH in labels:
        return MailboxState.TRASH
    if LABEL_DRAFT in labels:
        return MailboxState.DRAFT
    if LABEL_SENT in labels:
        return MailboxState.SENT
    if LABEL_INBOX in labels:
        return MailboxState.ACTIVE_INBOX
    # No INBOX and none of the above: the message was removed from the
    # inbox (archived) or never had it.
    return MailboxState.ARCHIVED


class MailEligibilityPolicy:
    """One policy module for mailbox state, category, and pipeline rules."""

    # ── Pure derivations ────────────────────────────────────────────

    @staticmethod
    def mailbox_state(label_ids: list[str] | set[str] | None) -> MailboxState:
        return mailbox_state_from_labels(label_ids)

    @staticmethod
    def gmail_category(label_ids: list[str] | set[str] | None) -> GmailCategory:
        return gmail_category_from_labels(label_ids)

    # ── Display ─────────────────────────────────────────────────────

    @staticmethod
    def should_display_in_inbox(label_ids: list[str] | set[str] | None) -> bool:
        """Alfred's current Inbox shows active Gmail Inbox messages only."""
        return mailbox_state_from_labels(label_ids) == MailboxState.ACTIVE_INBOX

    # ── Pipeline ────────────────────────────────────────────────────

    @staticmethod
    def pipeline_eligibility(label_ids: list[str] | set[str] | None) -> PipelineEligibility:
        """ACTIVE / DEFERRED / EXCLUDED for the intelligence pipeline.

        - Spam, Trash, Draft, Sent-only, archived: EXCLUDED.
        - Promotions/Social (Gmail-classified) may be DEFERRED for lazy
          analysis, but they still count as pipeline-visible when the user
          opens them. They are not EXCLUDED from attention rules purely by
          category (category is not semantic truth) — the briefing policy
          applies the stronger filter.
        """
        labels = set(label_ids or [])
        state = mailbox_state_from_labels(labels)
        if state != MailboxState.ACTIVE_INBOX:
            return PipelineEligibility.EXCLUDED

        category = gmail_category_from_labels(labels)
        if category in LAZY_CATEGORIES and LABEL_IMPORTANT not in labels:
            return PipelineEligibility.DEFERRED
        return PipelineEligibility.ACTIVE

    @staticmethod
    def is_excluded(label_ids: list[str] | set[str] | None) -> bool:
        return mailbox_state_from_labels(label_ids) != MailboxState.ACTIVE_INBOX

    @staticmethod
    def is_important_gmail(label_ids: list[str] | set[str] | None) -> bool:
        return LABEL_IMPORTANT in set(label_ids or [])

    @staticmethod
    def is_unread(label_ids: list[str] | set[str] | None) -> bool:
        return LABEL_UNREAD in set(label_ids or [])

    # ── Briefing / attention ────────────────────────────────────────

    @staticmethod
    def should_include_in_briefing(label_ids: list[str] | set[str] | None,
                                   analysis_priority: str | None = None,
                                   needs_reply: bool | None = None) -> bool:
        """Default briefing candidates: active inbox, not spam/trash/draft/
        sent-only, and not a low-value tab unless strong attention signals
        exist (Gmail IMPORTANT, urgent/high analysis, or a required reply).
        """
        labels = set(label_ids or [])
        if mailbox_state_from_labels(labels) != MailboxState.ACTIVE_INBOX:
            return False
        category = gmail_category_from_labels(labels)
        if category in LAZY_CATEGORIES:
            strong_signal = (
                LABEL_IMPORTANT in labels
                or analysis_priority in ("urgent", "high")
                or needs_reply
            )
            if not strong_signal:
                return False
        return True

    @staticmethod
    def should_include_in_attention(label_ids: list[str] | set[str] | None) -> bool:
        """Important/Needs-Reply attention projections require active inbox."""
        return mailbox_state_from_labels(label_ids) == MailboxState.ACTIVE_INBOX

    # ── Analysis scheduling ─────────────────────────────────────────

    # Higher number = processed earlier (matches jobs.priority DESC).
    SCHEDULING_PRIORITY = {
        (GmailCategory.PRIMARY, True): 100,   # P0: Gmail IMPORTANT Primary
        (GmailCategory.PRIMARY, False): 80,   # P1: Primary
        (GmailCategory.UPDATES, False): 60,   # P2: Updates
        (GmailCategory.FORUMS, False): 40,    # P3: Forums
        (GmailCategory.SOCIAL, False): 20,    # P4: Social
        (GmailCategory.PROMOTIONS, False): 10,  # P5: Promotions
    }

    @classmethod
    def analysis_queue_priority(cls, label_ids: list[str] | set[str] | None,
                                unread: bool = False,
                                known_thread: bool = False) -> int:
        """Processing order for the background analysis queue.

        This is PROCESSING ORDER, not final Alfred priority.
        """
        labels = set(label_ids or [])
        category = gmail_category_from_labels(labels)
        gmail_important = LABEL_IMPORTANT in labels
        if gmail_important:
            return 100
        if unread and category == GmailCategory.PRIMARY:
            return 95
        if known_thread:
            return 90
        key = (category, False)
        return cls.SCHEDULING_PRIORITY.get(key, 50)

    @classmethod
    def should_schedule_analysis(cls, label_ids: list[str] | set[str] | None,
                                 user_requested: bool = False) -> bool:
        """Whether a message should be enqueued for background analysis.

        Spam/Trash/Draft/Sent-only/archived are never scheduled.
        Promotions/Social are lazily scheduled: only when the user opens
        them, explicitly requests analysis, or Gmail marks them IMPORTANT.
        """
        labels = set(label_ids or [])
        state = mailbox_state_from_labels(labels)
        if state != MailboxState.ACTIVE_INBOX:
            return False
        category = gmail_category_from_labels(labels)
        if category in LAZY_CATEGORIES:
            return user_requested or LABEL_IMPORTANT in labels
        return True
