"""Task derivation service for Alfred.

Extracts genuine user tasks from AI analysis results.
Applies ownership validation, noise filtering, deduplication, and confidence scoring.

A task exists ONLY when there is evidence that THE USER is expected to do something.
"""
import hashlib
import re
from dataclasses import dataclass
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
            pass  # thread was never scoped â€” nothing legacy to cover
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
    Does NOT persist anything â€” caller is responsible for storage.
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


@dataclass
class ReconcileReport:
    """What a reconcile actually did, in the terms the migration contract uses.

    Every pre-existing task lands in exactly one bucket, so a run can be
    audited rather than trusted.
    """

    before: int = 0
    after: int = 0
    preserved: int = 0      # already matched current logic, untouched
    normalized: int = 0     # matched, but a field was corrected
    recreated: int = 0      # no stored row matched, so a new one was written
    removed: int = 0        # current logic rejects it and the user never touched it
    duplicates: int = 0     # a second row for a task we already keep
    kept_user_state: int = 0  # rejected by the extractor but completed/dismissed
    linked: int = 0         # resulting tasks that carry source linkage
    unlinked: int = 0       # resulting tasks with no source email

    def as_dict(self) -> dict:
        return {
            "before": self.before, "after": self.after,
            "preserved": self.preserved, "normalized": self.normalized,
            "recreated": self.recreated, "removed": self.removed,
            "duplicates": self.duplicates,
            "kept_user_state": self.kept_user_state,
            "linked": self.linked, "unlinked": self.unlinked,
        }


# Fields the extractor owns. A difference in any of them means the stored row
# is stale and the reconcile must correct it. `status`, `created_at` and
# `priority_override` are deliberately absent: those belong to the user.
# `derivation_version` is included so a row that is otherwise correct still gets
# stamped with the version that produced it - otherwise an unchanged row keeps a
# stale version forever and a future version-filtered migration would miss it.
_DERIVED_FIELDS = ("title", "description", "due_at", "owner", "priority",
                   "source_email_id", "source_thread_id", "derivation_version")


def _is_derived_change(new: Task, existing: Task) -> bool:
    return any(getattr(new, f, None) != getattr(existing, f, None)
               for f in _DERIVED_FIELDS)


def reconcile_tasks_from_analyses(repo, model: str) -> ReconcileReport:
    """Make the tasks table match the current derivation logic. The one path.

    This is both the rebuild and the migration; there is deliberately no second
    implementation. It is safe to run on every startup and safe to run twice:

    * Every stored task is matched to the task the current logic derives from
      the same message, by fingerprint, honouring both the account-scoped and
      the legacy raw-thread fingerprint so a thread-id migration can never
      duplicate a task.
    * A matched row is *updated* rather than skipped, so a row written by an
      older derivation is corrected in place instead of lingering beside a
      fresh copy. This is what the previous implementation got wrong: it
      skipped any fingerprint already present and only deleted derivation
      version "1", so version "2" rows survived a logic change untouched.
    * ``status``, ``created_at`` and any ``priority_override`` are carried
      over from the stored row. The extractor never overwrites user intent.
    * A stored row the current logic no longer produces is removed **only if it
      is still ``pending``** - that is, only if the user never acted on it. A
      completed or dismissed row is kept, because the user's decision to close
      it is itself information.
    * Messages excluded from the pipeline (spam, trash, archived) contribute
      nothing, but their existing rows are reconciled like any other.

    Returns a :class:`ReconcileReport` describing what changed.
    """
    from ..db.database import transaction
    from ..mail.eligibility import MailEligibilityPolicy

    report = ReconcileReport()
    existing_rows = repo.tasks_all()
    report.before = len(existing_rows)

    # Index stored rows by every fingerprint they could be matched on.
    by_fp: dict[str, list[Task]] = {}
    for row in existing_rows:
        fp = getattr(row, "fingerprint", None)
        if fp:
            by_fp.setdefault(fp, []).append(row)

    # Deterministic order: the same analyses must always yield the same plan.
    pairs = sorted(repo.all_analyses_with_emails(model), key=lambda p: p[0].id)

    produced: list[Task] = []
    produced_candidates: dict[int, list[str]] = {}
    claimed: set[str] = set()
    for email, analysis in pairs:
        if MailEligibilityPolicy.pipeline_eligibility(email.label_ids) == "excluded":
            continue
        for task in derive_tasks(email, analysis):
            fp = getattr(task, "fingerprint", None)
            try:
                candidates = candidate_fingerprints(
                    email.thread_id, email.account_id,
                    _normalize_action(task.title or ""))
            except Exception:
                candidates = [fp] if fp else []
            candidates = [c for c in candidates if c]
            # Cross-message dedupe, and the guard that makes a second run a
            # no-op: a fingerprint already claimed in this pass is skipped.
            if any(c in claimed for c in candidates):
                continue
            claimed.update(candidates)
            produced_candidates[id(task)] = candidates
            produced.append(task)

    matched_ids: set[str] = set()
    matched_fps: set[str] = set()
    to_write: list[Task] = []
    to_delete: list[str] = []

    for task in produced:
        hit = None
        for c in produced_candidates.get(id(task), []):
            rows = by_fp.get(c)
            if rows:
                # Deterministic winner when a fingerprint is duplicated. A row
                # the user has acted on always beats an untouched one, then the
                # older row wins, then id - so the result never depends on row
                # order or on which run created the copy.
                hit = sorted(rows, key=lambda r: (
                    r.status != "pending", r.created_at or "", r.id))[0]
                break
        if hit is None:
            to_write.append(task)
            report.recreated += 1
            continue

        if hit.id in matched_ids:
            # A second stored row for a task we already matched.
            if hit.status == "pending":
                to_delete.append(hit.id)
                report.duplicates += 1
            else:
                report.kept_user_state += 1
            continue

        matched_ids.add(hit.id)
        matched_fps.update(produced_candidates.get(id(task), []))
        merged = task.model_copy()
        merged.id = hit.id
        merged.status = hit.status
        merged.created_at = hit.created_at
        if getattr(hit, "priority_override", None):
            merged.priority = hit.priority
            merged.priority_override = hit.priority_override
        if _is_derived_change(merged, hit):
            to_write.append(merged)
            report.normalized += 1
        else:
            report.preserved += 1

    for row in existing_rows:
        if row.id in matched_ids or row.id in to_delete:
            continue
        # The current logic no longer produces this task. If its fingerprint is
        # one we just matched, it is a duplicate of a task we are keeping rather
        # than an invalid extraction, and the report must say so.
        is_duplicate = bool(getattr(row, "fingerprint", None)) and \
            getattr(row, "fingerprint", None) in matched_fps
        if row.status == "pending":
            to_delete.append(row.id)
            if is_duplicate:
                report.duplicates += 1
            else:
                report.removed += 1
        else:
            report.kept_user_state += 1

    with transaction(repo.con) as cur:
        for task in to_write:
            cur.execute(
                """INSERT INTO tasks (id, source_email_id, source_thread_id, title,
                   description, due_at, owner, priority, status, created_at,
                   derivation_version, confidence, fingerprint, priority_override)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(id) DO UPDATE SET
                     source_email_id=excluded.source_email_id,
                     source_thread_id=excluded.source_thread_id,
                     title=excluded.title, description=excluded.description,
                     due_at=excluded.due_at, owner=excluded.owner,
                     priority=excluded.priority, derivation_version=excluded.derivation_version,
                     confidence=excluded.confidence, fingerprint=excluded.fingerprint""",
                (task.id, task.source_email_id, task.source_thread_id, task.title,
                 task.description, task.due_at, task.owner, task.priority,
                 # status and created_at are supplied by the stored row for an
                 # update; for a genuinely new row these are the derived values.
                 task.status or "pending",
                 task.created_at or datetime.now(timezone.utc).isoformat(),
                 getattr(task, "derivation_version", DERIVATION_VERSION),
                 getattr(task, "confidence", "medium"),
                 getattr(task, "fingerprint", None),
                 getattr(task, "priority_override", None)),
            )
        for task_id in to_delete:
            cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))

    report.after = len(repo.tasks_all())
    for row in repo.tasks_all():
        if row.source_email_id:
            report.linked += 1
        else:
            report.unlinked += 1
    return report


def rebuild_tasks_from_analyses(repo, model: str) -> int:
    """Back-compatible wrapper. Prefer :func:`reconcile_tasks_from_analyses`.

    Kept because startup calls it by name; it is a thin alias, not a second
    implementation, so there is still exactly one authoritative path.
    """
    return reconcile_tasks_from_analyses(repo, model).recreated


