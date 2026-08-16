"""Task derivation service for Alfred.

Extracts genuine user tasks from AI analysis results.
Applies ownership validation, noise filtering, deduplication, and confidence scoring.

A task exists ONLY when there is evidence that THE USER is expected to do something.
"""
import hashlib
import re
from datetime import datetime, timezone
from ..schemas import Email, EmailAnalysis, ActionItem, Task


DERIVATION_VERSION = "2"

# Patterns that indicate noise, not real user tasks
NOISE_PATTERNS = [
    re.compile(r"decode\s+(the\s+)?base64", re.I),
    re.compile(r"verify\s+(the\s+)?(user.?s?|your)\s+(tiktok|instagram|facebook|twitter|account)\s+(account\s+)?credentials?", re.I),
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


def _normalize_action(description: str) -> str:
    """Normalize action text for deduplication."""
    text = description.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    # Remove trailing punctuation
    text = text.rstrip('.!?;:')
    return text


def task_fingerprint(thread_id: str | None, normalized_action: str, deadline: str | None) -> str:
    """Create a stable fingerprint for task deduplication."""
    payload = f"{thread_id or ''}|{normalized_action}|{deadline or ''}"
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]


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
    
    for idx, item in enumerate(analysis.action_items):
        # Validate this is a genuine user task
        if not _is_user_actionable(item, email, analysis):
            continue
        
        normalized = _normalize_action(item.description)
        fp = task_fingerprint(email.thread_id, normalized, item.deadline)
        
        # Skip duplicates within this email
        if fp in seen_fingerprints:
            continue
        seen_fingerprints.add(fp)
        
        confidence = _assign_confidence(item, analysis)
        
        task = Task(
            id=f"task_{email.id}_{idx}",
            source_email_id=email.id,
            source_thread_id=email.thread_id,
            title=item.description,
            description=f"Owner: {item.owner}" if item.owner else None,
            due_at=item.deadline,
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
        normalized = _normalize_action(dl.description)
        fp = task_fingerprint(email.thread_id, normalized, dl.due_at)
        
        if fp in seen_fingerprints:
            continue
        
        # Apply same noise filtering
        if _is_noise(dl.description):
            continue
        if len(dl.description.strip()) < MIN_TASK_LENGTH:
            continue
        
        # Only add deadline-tasks for explicit deadlines
        if dl.confidence != "explicit":
            continue
        
        seen_fingerprints.add(fp)
        
        task = Task(
            id=f"deadline_{email.id}_{idx}",
            source_email_id=email.id,
            source_thread_id=email.thread_id,
            title=dl.description,
            description=f"Due: {dl.due_at}" if dl.due_at else None,
            due_at=dl.due_at,
            priority=analysis.priority.value,
            status='pending',
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        task.derivation_version = DERIVATION_VERSION  # type: ignore
        task.confidence = "high" if dl.due_at else "medium"  # type: ignore
        task.fingerprint = fp  # type: ignore
        
        candidates.append(task)
    
    return candidates


def rebuild_tasks_from_analyses(repo, model: str):
    """Rebuild all derived tasks from cached analyses using the current derivation logic.
    
    This is the safe migration path:
    1. Delete all tasks from old derivation versions
    2. Re-derive from cached analyses (no Ollama re-invocation needed)
    3. Preserve user-modified task statuses where possible
    """
    # Delete old auto-derived tasks
    repo.delete_tasks_by_derivation_version("1")
    
    # Re-derive from all cached analyses
    pairs = repo.all_analyses_with_emails(model)
    all_new_tasks = []
    global_fingerprints = set()
    
    for email, analysis in pairs:
        tasks = derive_tasks(email, analysis)
        for task in tasks:
            fp = getattr(task, 'fingerprint', None)
            if fp and fp in global_fingerprints:
                continue  # Cross-email deduplication
            if fp:
                global_fingerprints.add(fp)
            # Also check if this fingerprint already exists in DB
            if fp and repo.task_exists_by_fingerprint(fp):
                continue
            all_new_tasks.append(task)
    
    if all_new_tasks:
        repo.save_tasks_batch(all_new_tasks)
    
    return len(all_new_tasks)
