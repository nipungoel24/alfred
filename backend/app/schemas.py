from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class Priority(str, Enum): urgent="urgent"; high="high"; medium="medium"; low="low"
class Category(str, Enum): work="work"; personal="personal"; finance="finance"; travel="travel"; meeting="meeting"; notification="notification"; newsletter="newsletter"; promotion="promotion"; security="security"; other="other"
class ActionItem(BaseModel):
    description: str = Field(description="Description of the action item.")
    owner: str | None = Field(None, description="The person responsible for the action item, if explicitly mentioned.")
    deadline: str | None = Field(None, description="The deadline for the action item as a raw string (e.g., 'Friday' or '5 PM today'), if explicitly mentioned.")

class Deadline(BaseModel):
    description: str = Field(description="Description of the task or action that has a deadline.")
    due_at: str | None = Field(None, description="The explicit date/time when it is due (e.g. '5 PM today', 'Friday', '2026-08-16'). Do NOT invent precise dates if not mentioned.")
    confidence: str = Field("explicit", description="Confidence level of the deadline extraction: 'explicit' or 'inferred'.")

class ImportantEntity(BaseModel): type: str; value: str
class EmailAnalysis(BaseModel):
    short_summary: str; category: Category; priority: Priority; priority_score: int = Field(ge=0, le=100)
    reason_for_priority: str; needs_reply: bool
    action_items: list[ActionItem] = Field(default_factory=list, description="List of individual actions required.")
    deadlines: list[Deadline] = Field(default_factory=list, description="List of deadlines explicitly mentioned in the email (e.g. 'by Friday', 'before 5 PM today'). Keep empty if timing is ambiguous (like 'soon', 'asap') or missing.")
    important_entities: list[ImportantEntity] = Field(default_factory=list); important_details: list[str] = Field(default_factory=list)
class Email(BaseModel):
    id: str; thread_id: str | None = None; sender: str; sender_name: str | None = None; recipients: list[str] = Field(default_factory=list)
    subject: str; body: str; received_at: datetime | None = None; source_metadata: dict[str, Any] = Field(default_factory=dict)
    analysis: EmailAnalysis | None = None
class BriefingItem(BaseModel): email_id: str; sender: str; subject: str; short_summary: str; priority: Priority; why_it_matters: str; deadline: str | None = None; needs_reply: bool
class InboxBriefing(BaseModel):
    executive_summary: str; total_emails: int; urgent_count: int; high_priority_count: int; needs_reply_count: int; deadline_count: int
    top_attention_items: list[BriefingItem] = Field(default_factory=list); deadlines: list[BriefingItem] = Field(default_factory=list); important_updates: list[str] = Field(default_factory=list); can_wait_or_review_later: list[str] = Field(default_factory=list)
class ErrorDetail(BaseModel): code: str; message: str; details: dict[str, Any] = {}
