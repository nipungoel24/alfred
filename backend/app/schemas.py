from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field, field_validator

from .services.due_dates import is_relative_expression, normalize_due_at


def _clean_due(value: object) -> str | None:
    """Reduce a model-supplied due value to a stored instant, or keep a
    relative form that derivation can resolve against the message timestamp.

    The schema is validated on its own, with no access to the message, so an
    absolute date is normalised here and a relative offset is passed through
    untouched. Everything else - field labels, vague prose, bare clock times -
    becomes None and never reaches the database.
    """
    resolved = normalize_due_at(value)
    if resolved is not None:
        return resolved
    return value if is_relative_expression(value) else None

class Priority(str, Enum): urgent="urgent"; high="high"; medium="medium"; low="low"
class Category(str, Enum): work="work"; personal="personal"; finance="finance"; travel="travel"; meeting="meeting"; notification="notification"; newsletter="newsletter"; promotion="promotion"; security="security"; other="other"

# These field descriptions are not documentation for us â€” they are shipped to
# the model verbatim as part of `model_json_schema()`. They used to invite the
# model to answer with prose ("Friday", "5 PM today"), which is how "due_at:
# soon" and "15 minutes from now" ended up stored as due dates. The contract
# is now an absolute ISO-8601 timestamp or null, and nothing else.
_DUE_CONTRACT = (
    "Absolute due moment as ISO-8601 (e.g. '2026-09-12T00:00:00+00:00'), or null "
    "when the email states no definite moment. Never prose ('soon', 'asap', "
    "'at the earliest', '15 minutes from now'), never a clock time without a "
    "date, and never a field label such as 'due_at:'. Use null rather than guess."
)

class ActionItem(BaseModel):
    description: str = Field(description="The action THE RECIPIENT must take, in your own words. Never a date, a time, a field label, or a statement that no action is required.")
    owner: str | None = Field(None, description="The person responsible for the action item, if explicitly mentioned.")
    deadline: str | None = Field(None, description=_DUE_CONTRACT)

    _norm_deadline = field_validator("deadline", mode="before")(_clean_due)

class Deadline(BaseModel):
    description: str = Field(description="The action the deadline applies to. Must describe something to DO â€” never a bare date, time, or relative phrase on its own.")
    due_at: str | None = Field(None, description=_DUE_CONTRACT)
    confidence: str = Field("explicit", description="Confidence level of the deadline extraction: 'explicit' or 'inferred'.")

    _norm_due_at = field_validator("due_at", mode="before")(_clean_due)


class EmailAnalysis(BaseModel):
    short_summary: str; category: Category; priority: Priority; priority_score: int = Field(ge=0, le=100)
    reason_for_priority: str; needs_reply: bool
    action_items: list[ActionItem] = Field(default_factory=list, description="List of individual actions required.")
    deadlines: list[Deadline] = Field(default_factory=list, description="List of deadlines explicitly mentioned in the email (e.g. 'by Friday', 'before 5 PM today'). Keep empty if timing is ambiguous (like 'soon', 'asap') or missing.")
class Email(BaseModel):
    id: str; thread_id: str | None = None; account_id: str | None = None; sender: str; sender_name: str | None = None; recipients: list[str] = Field(default_factory=list)
    subject: str; body: str; received_at: datetime | None = None; source_metadata: dict[str, Any] = Field(default_factory=dict)
    label_ids: list[str] = Field(default_factory=list)
    analysis: EmailAnalysis | None = None
    # Provider-side message id (Gmail hex id). The primary key `id` is the
    # account-scoped local identity; this field preserves the provider id
    # for API calls and the (account_id, provider_message_id) uniqueness
    # invariant. None for legacy CSV imports.
    provider_message_id: str | None = None
class BriefingItem(BaseModel): email_id: str; sender: str; subject: str; short_summary: str; priority: Priority; why_it_matters: str; deadline: str | None = None; needs_reply: bool
class InboxBriefing(BaseModel):
    executive_summary: str; total_emails: int; urgent_count: int; high_priority_count: int; needs_reply_count: int; deadline_count: int
    top_attention_items: list[BriefingItem] = Field(default_factory=list); deadlines: list[BriefingItem] = Field(default_factory=list); important_updates: list[str] = Field(default_factory=list); can_wait_or_review_later: list[str] = Field(default_factory=list)
class ErrorDetail(BaseModel): code: str; message: str; details: dict[str, Any] = {}


# User-facing `in:` search scope -> stored mailbox_state.
# Internal enum names (active_inbox) are never exposed to users.
IN_SCOPE_TO_MAILBOX_STATE: dict[str, str | None] = {
    "inbox": "active_inbox",
    "archived": "archived",
    "sent": "sent",
    # "all" means no additional restriction beyond Alfred's normal
    # searchable states (active_inbox + archived + sent).
    "all": None,
}


class SearchFilters(BaseModel):
    """Structured search filters parsed from the frontend.

    Every field maps to a stored, indexed column or to the persisted
    analysis payload â€” no operator is advertised that cannot truly work.
    """
    free_text: list[str] = Field(default_factory=list)
    sender: str | None = None
    subject: str | None = None
    is_unread: bool | None = None
    is_read: bool | None = None
    is_important: bool | None = None
    needs_reply: bool | None = None
    after: str | None = None
    before: str | None = None
    category: str | None = None
    mailbox_state: str | None = None

    @field_validator("mailbox_state")
    @classmethod
    def _resolve_mailbox_state(cls, value: str | None) -> str | None:
        """Map the user-facing `in:` scope to storage, strictly.

        Accepted: inbox, archived, sent, all (all -> None = no extra
        restriction). Anything else is a controlled 422 validation error â€”
        the frontend parser keeps unknown `in:` values as free text so
        typos never reach this error path in normal use.
        """
        if value is None:
            return None
        key = value.strip().lower()
        if key not in IN_SCOPE_TO_MAILBOX_STATE:
            raise ValueError(
                f"Unknown search scope: {value!r}. "
                f"Use one of: inbox, all, archived, sent."
            )
        return IN_SCOPE_TO_MAILBOX_STATE[key]


class EmailAccount(BaseModel):
    id: str
    provider: str
    email_address: str
    display_name: str | None = None
    connection_status: str # 'connected', 'disconnected', 'error'
    last_sync_at: str | None = None
    sync_cursor: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

class Task(BaseModel):
    id: str
    source_email_id: str | None = None
    source_thread_id: str | None = None
    title: str
    description: str | None = None
    # Normalised ISO-8601 instant, or null. Never prose: see
    # services.due_dates.normalize_due_at for what is rejected and why.
    due_at: str | None = None
    # Who is responsible. A first-class field, not a line inside `description`:
    # encoding "Owner: user" as prose meant every consumer had to re-parse it.
    owner: str | None = None
    priority: str | None = None
    status: str # 'pending', 'completed', 'dismissed'
    created_at: str | None = None
    derivation_version: str = "1"
    confidence: str = "medium"
    fingerprint: str | None = None
    # Explicit user-set priority. Derivation and migration must never
    # overwrite priority while this is set â€” the user corrected Alfred.
    priority_override: str | None = None


class TaskPriorityPatch(BaseModel):
    """Validated priority edit for one task (task only — never rewrites
    the source email's AI analysis)."""
    priority: Priority


class ModelSelectRequest(BaseModel):
    """Which local model Alfred should use for analysis."""
    model: str = Field(..., min_length=1, description="Ollama model tag, e.g. qwen3:4b")


class ModelPullRequest(BaseModel):
    """A download target. Omitted means the currently configured model."""
    model: str | None = Field(None, min_length=1, description="Ollama model tag to download")

