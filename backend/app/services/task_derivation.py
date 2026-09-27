"""Task derivation service for Alfred.

Extracts genuine user tasks from AI analysis results.
Applies ownership validation, noise filtering, deduplication, and confidence scoring.

A task exists ONLY when there is evidence that THE USER is expected to do something.
"""
import hashlib
import re
from datetime import datetime, timezone
from ..schemas import Email, EmailAnalysis, ActionItem, Task
from .due_dates import is_non_action, is_temporal_only, normalize_due_at


DERIVATION_VERSION = "3"

# Patterns that indicate noise, not real user tasks
NOISE_PATTERNS = [
    re.compile(r"decode\s+(the\s+)?base64", re.I),
    re.compile(r"(verify|check)\s+(the\s+)?(user.?s?\s+|your\s+)?(tiktok|instagram|facebook|twitter|account|identity)\s+(account\s+)?credentials?", re.I),
    re.compile(r"verify\s+(your\s+)?identity", re.I),
    re.compile(r"transfer\s+\$100", re.I),
    re.compile(r"(move|reschedule)\s+(the\s+)?(daily\s+)?(standup|meeting)", re.I),
    re.compile(r"check\s+if\s+(the\s+)?user\s+has\s+a?\s*pending\s+password\s+reset", re.I),
    re.compile(r"(click|tap)\s+(here|below|the\s+link|the\s+button)", re.I),
    re.compile(r"(buy|shop|purchase|order)\s+now", re.I),
    re.compile(r"(unsubscribe|manage\s+preferences|opt\s+out)", re.I),
    re.compile(r"(complete|verify|confirm)\s+your\s+(profile|account|registration|email)", re.I),
    re.compile(r"(download|install|upgrade)\s+(the\s+)?(app|software|update)", re.I),
    re.compile(r"reveal\s+(the\s+)?(user.s?|your)\s+credentials?", re.I),
    re.compile(r"execute\s+(it|this|the\s+command)", re.I),
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions?", re.I),
    re.compile(r"send\s+(the\s+)?(user.s?|your)\s+credentials?\s+to", re.I),
    re.compile(r"update\s+payment\s+method", re.I),
    re.compile(r"(flight|travel|meeting)\s+(schedule\s+)?(change|delay|update)", re.I),
    re.compile(r"receipt|invoice", re.I),
    re.compile(r"review\s+recent\s+activity", re.I),
    # One-time codes are not work. "Enter GitHub sudo authentication code"
    # came from an automated security notification. The gap allows a product or
    # vendor name between the verb and the noun ("Enter GitHub sudo ... code").
    re.compile(r"\b(enter|use|input|supply|provide)\b[^,.;:]{0,48}?"
               r"\b(code|password|pin|otp|passcode|one[-\s]?time\s+code)\b", re.I),
    # Marketing CTAs: joining a community channel is not the recipient's work.
    re.compile(r"join\s+.*\b(whatsapp|telegram|discord|slack)\b.*\b(channel|group|community)\b", re.I),
    re.compile(r"join\s+the\s+.*\b(channel|community|group)\b", re.I),
    # Conditional support CTAs attached to an automated receipt.
    re.compile(r"contact\s+\w+\s+if\s+.*\b(error|issue|problem|incorrect)\b.*\b(notice|notice[d]?|see|found)\b", re.I),
]

# Categories that should rarely generate user tasks
LOW_TASK_CATEGORIES = {"newsletter", "promotion", "notification"}

# Minimum description length for a valid task
MIN_TASK_LENGTH = 10


def _is_noise(description: str) -> bool:
    """Check if a task description matches known noise patterns."""
    for pattern in NOISE_PATTERNS:
        if pattern.search(description):
            return True
    return False


def _is_user_actionable(item: ActionItem, email: Email, analysis: EmailAnalysis) -> bool:
    """Determine if an action item is genuinely assigned to the user."""
    desc = item.description.strip()
    
    # Too short to be meaningful
    if len(desc) < MIN_TASK_LENGTH:
        return False

    # "No action required" is the model stating there is NO task. It used to
    # become a task titled "No action required".
    if is_non_action(desc):
        return False

    # A date, a clock time, or a leaked field label is not an action. These
    # became task titles such as "12th September 2026" and "due_at: soon".
    if is_temporal_only(desc):
        return False

    # Known noise
    if _is_noise(desc):
        return False
    
    # Owner is explicitly someone else (not the user)
    if item.owner and item.owner.lower() not in ("user", "me", "you", "recipient", ""):
        # If owner is a third party, this is likely not a user task
        # Unless the email is specifically asking the user to relay/coordinate
        return False
    
    # Newsletter/promotional/notification emails rarely have real tasks
    if analysis.category.value in LOW_TASK_CATEGORIES:
        # Only allow if priority is high/urgent AND needs_reply
        if not (analysis.priority.value in ("urgent", "high") and analysis.needs_reply):
            return False
    
    # Receipts are informational
    if "receipt" in analysis.category.value.lower():
        return False
    
    return True


def _reference(email: Email) -> datetime | None:
    """The timestamp relative wording is resolved against, when we have one."""
    return email.received_at if isinstance(email.received_at, datetime) else None


def _normalize_action(description: str) -> str:
    """Normalize action text for deduplication."""
    text = description.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    # Remove trailing punctuation
    text = text.rstrip('.!?;:')
    return text


def task_fingerprint(thread_id: str | None, normalized_action: str) -> str:
    """Create a stable fingerprint for task deduplication.
    We omit the deadline so that updates in the same thread overwrite the old deadline.
    """
    payload = f"{thread_id or ''}|{normalized_action}"
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]


def candidate_fingerprints(thread_id: str | None, account_id: str | None,
                           normalized_action: str) -> list[str]:
    """All fingerprints under which a task for this action may be stored.

    The thread-identity migration (raw provider thread id -> account-scoped
    local thread id) changed fingerprints for the same logical action.
    Callers must treat a task as existing when ANY candidate matches, so a
    re-derivation after migration never duplicates a pre-migration task.
    """
    fps = [task_fingerprint(thread_id, normalized_action)]
    if thread_id and account_id:
        try:
            from ..mail.identity import strip_scope
            raw_thread = strip_scope(thread_id, account_id)
            legacy = task_fingerprint(raw_thread, normalized_action)
            if legacy not in fps:
                fps.append(legacy)
        except ValueError:
            pass  # thread was never scoped — nothing legacy to cover
    return fps


def _assign_confidence(item: ActionItem, analysis: EmailAnalysis) -> str:
    """Assign confidence level to a derived task."""
    # Direct requests with explicit deadlines get high confidence
    if analysis.needs_reply and item.deadline:
        return "high"
    
    # Direct requests without deadlines
    if analysis.needs_reply:
        return "high"
    
    # Action items from high-priority emails
    if analysis.priority.value in ("urgent", "high"):
        return "medium"
    
    return "low"


def derive_tasks(email: Email, analysis: EmailAnalysis) -> list[Task]:
    """Derive genuine user tasks from an email analysis.
    
    Returns a deduplicated list of tasks with confidence scores and fingerprints.
    Does NOT persist anything — caller is responsible for storage.
    """
    candidates: list[Task] = []
    seen_fingerprints: set[str] = set()
    reference = _reference(email)

    for idx, item in enumerate(analysis.action_items):
        # Validate this is a genuine user task
        if not _is_user_actionable(item, email, analysis):
            continue
        
        normalized = _normalize_action(item.description)
        fp = task_fingerprint(email.thread_id, normalized)
        
        # Skip duplicates within this email
        if fp in seen_fingerprints:
            continue
        seen_fingerprints.add(fp)
        
        confidence = _assign_confidence(item, analysis)
        
        task = Task(
            id=f"task_{fp}",
            source_email_id=email.id,
            source_thread_id=email.thread_id,
            title=item.description.strip(),
            description=None,
            # Re-normalised against the message timestamp so a relative form
            # can still resolve here, where the reference finally exists.
            due_at=normalize_due_at(item.deadline, reference=reference),
            owner=item.owner or None,
            priority=analysis.priority.value,
            status='pending',
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        # Attach extra attributes for storage
        task.derivation_version = DERIVATION_VERSION  # type: ignore
        task.confidence = confidence  # type: ignore
        task.fingerprint = fp  # type: ignore
        
        candidates.append(task)
    
    # Deadlines that are NOT already represented by action items
    for idx, dl in enumerate(analysis.deadlines):
        desc = dl.description.strip()
        if not desc:
            continue

        normalized = _normalize_action(desc)
        fp = task_fingerprint(email.thread_id, normalized)
        
        if fp in seen_fingerprints:
            continue
        
        # Apply same noise filtering
        if _is_noise(desc):
            continue
        if len(desc) < MIN_TASK_LENGTH:
            continue

        # A deadline is a task only if it names something TO DO. "15 minutes
        # from now" and "12th September 2026" describe no action, so they are
        # dropped rather than becoming a task with the phrase as its title.
        if is_non_action(desc) or is_temporal_only(desc):
            continue
        
        # Only add deadline-tasks for explicit deadlines
        if dl.confidence != "explicit":
            continue
        
        due_at = normalize_due_at(dl.due_at, reference=reference)
        # An "explicit" deadline we cannot read as a real moment is not a
        # deadline. The prose is not preserved anywhere.
        if due_at is None:
            continue
        
        seen_fingerprints.add(fp)
        
        task = Task(
            id=f"deadline_{email.id}_{idx}",
            source_email_id=email.id,
            source_thread_id=email.thread_id,
            title=desc,
            description=None,
            due_at=due_at,
            owner=None,
            priority=analysis.priority.value,
            status='pending',
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        task.derivation_version = DERIVATION_VERSION  # type: ignore
        task.confidence = "high"  # type: ignore
        task.fingerprint = fp  # type: ignore
        
        candidates.append(task)
    
    return candidates


def rebuild_tasks_from_analyses(repo, model: str):
    """Rebuild all derived tasks from cached analyses using the current derivation logic.
    
    This is the safe migration path:
    1. Delete all tasks from old derivation versions
    2. Re-derive from cached analyses (no Ollama re-invocation needed)
    3. Preserve user-modified task statuses where possible

    Pipeline-ineligible source mail (spam/trash/archived) never produces
    new tasks during rebuild — stale analyses stay cached but hidden.
    """
    from ..mail.eligibility import MailEligibilityPolicy

    # Delete old auto-derived tasks
    repo.delete_tasks_by_derivation_version("1")
    
    # Re-derive from all cached analyses
    pairs = repo.all_analyses_with_emails(model)
    all_new_tasks = []
    global_fingerprints = set()
    
    for email, analysis in pairs:
        if MailEligibilityPolicy.pipeline_eligibility(email.label_ids) == 'excluded':
            continue
        tasks = derive_tasks(email, analysis)
        for task in tasks:
            fp = getattr(task, 'fingerprint', None)
            # A task counts as existing when ANY candidate fingerprint
            # matches (current scoped-thread form or legacy raw-thread form),
            # so the thread migration can never duplicate a task here either.
            try:
                candidates = candidate_fingerprints(
                    email.thread_id, email.account_id,
                    _normalize_action(task.title or ''))
            except Exception:
                candidates = [fp] if fp else []
            if fp and fp in global_fingerprints:
                continue  # Cross-email deduplication
            if any(c in global_fingerprints for c in candidates if c):
                continue
            for c in candidates:
                if c:
                    global_fingerprints.add(c)
            # Also check if this fingerprint already exists in DB
            if any(c and repo.task_exists_by_fingerprint(c) for c in candidates if c):
                continue
            all_new_tasks.append(task)
    
    if all_new_tasks:
        repo.save_tasks_batch(all_new_tasks)
    
    return len(all_new_tasks)
