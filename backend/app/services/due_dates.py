"""Due-date normalisation for extracted tasks.

The extraction model used to be *told* to keep relative wording in the due
field, and the schema typed that field as a free-form ``str``. Both have been
removed, but the old rows are still in the database, so this module is the
single place that decides what a due value is allowed to be.

The rule is deliberately strict: a due date is either a real, normalised
ISO-8601 timestamp, or ``None``. Anything the model produced that cannot be
read as a definite moment in time â€” vague prose ("soon", "at the earliest"),
a leaked field label ("due_at: soon"), a bare clock time, or free text â€” is
dropped rather than guessed at. A missing due date is honest; an invented one
is not.

Relative expressions are the one case where the source wording is resolved
against a real timestamp, and only when the caller supplies that reference
(the email's ``received_at``). Without a reference they stay ``None``.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone

__all__ = [
    "normalize_due_at",
    "is_relative_expression",
    "is_temporal_only",
    "is_non_action",
    "VAGUE_DUE_PHRASES",
]


# A leaked extraction field label, e.g. the model emitting the string
# "due_at: soon" or "Deadline:" as the *value* of a due field. A due value
# that begins with a field name is never a date.
_FIELD_LABEL_RE = re.compile(
    r"^\s*(due_at|due|deadline|deadline_at|priority|owner|status|title|"
    r"action|action_item|description)\s*[:\-]\s*",
    re.I,
)
# The same label with nothing after it ("due_at" on its own).
_FIELD_LABEL_BARE_RE = re.compile(
    r"^\s*(due_at|due|deadline|deadline_at|priority|owner|status)\s*:?\s*$", re.I
)

# Wording that names a timeframe without naming a moment. Never a due date.
VAGUE_DUE_PHRASES = (
    "soon",
    "asap",
    "as soon as possible",
    "at the earliest",
    "the earliest",
    "earliest",
    "at the latest",
    "the latest",
    "latest",
    "shortly",
    "briefly",
    "later",
    "sometime",
    "some time",
    "next few days",
    "few days",
    "a few days",
    "in a few days",
    "coming soon",
    "later today",
    "today",
    "tonight",
    "tomorrow",
    "yesterday",
    "this week",
    "next week",
    "end of day",
    "eod",
    "cob",
    "close of business",
    "immediately",
    "right away",
    "now",
    "tba",
    "tbd",
    "to be decided",
    "to be determined",
    "n/a",
    "na",
    "none",
    "null",
    "nil",
    "unknown",
    "unspecified",
    "not specified",
    "no deadline",
    "no due date",
    "no action required",
    "nothing to do",
    "optional",
    "whenever",
    "whenever possible",
    "when possible",
)

_VAGUE_RE = re.compile(
    r"^\s*(?:" + "|".join(re.escape(p) for p in sorted(VAGUE_DUE_PHRASES, key=len, reverse=True)) + r")\s*[.!]?\s*$",
    re.I,
)

# Phrases that assert there is no actionable work. The model emits these while
# meaning "this email needs nothing from you"; they must never become a task.
_NON_ACTION_RE = re.compile(
    r"^\s*(?:no\s+(?:action|response|task|work|reply|follow[- ]?up)\s*(?:is\s+)?"
    r"(?:required|needed|necessary)?|nothing\s+(?:to|needs?)\s+(?:do|be\s+done)|"
    r"n/?a|none|no\s+tasks?)\s*[.!]?\s*$",
    re.I,
)

_MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}
_MONTH_ALT = "|".join(sorted(_MONTHS, key=len, reverse=True))

# A bare clock time ("11:00 AM", "17:30") names no day, so it is never a due
# date and never a task title.
_BARE_TIME_RE = re.compile(
    r"^\s*(?:[01]?\d|2[0-3])[:.][0-5]\d\s*(?:[ap]\.?m\.?)?\s*$", re.I
)
# A trailing weekday gloss, e.g. "Sep 11th, 2026 (Friday)".
_WEEKDAY_GLOSS_RE = re.compile(
    r"\(?\b(?:mon|tue|tues|wed|thu|thur|thurs|fri|sat|sun)(?:day|nesday|rsday|urday)?\b\)?",
    re.I,
)

_ORDINAL_SUFFIX_RE = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)\b", re.I)

# "12 September 2026", "12th September, 2026", "September 12 2026"
_DMY_RE = re.compile(
    rf"\b(\d{{1,2}})\s*(?:st|nd|rd|th)?\s+({_MONTH_ALT})\.?\s*,?\s*(\d{{4}})\b", re.I
)
_MDY_RE = re.compile(
    rf"\b({_MONTH_ALT})\.?\s*(\d{{1,2}})\s*(?:st|nd|rd|th)?\s*,?\s*(\d{{4}})\b", re.I
)
# "September 12" with no year â€” only usable when a reference supplies one.
_DMY_NO_YEAR_RE = re.compile(
    rf"\b(\d{{1,2}})\s*(?:st|nd|rd|th)?\s+({_MONTH_ALT})\b", re.I
)
_MDY_NO_YEAR_RE = re.compile(rf"\b({_MONTH_ALT})\.?\s*(\d{{1,2}})\b(?!\s*,?\s*\d{{4}})", re.I)

# ISO date or datetime, optionally with a trailing ordinal-ish suffix removed.
_ISO_DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?)?")
_ISO_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")

# Relative offsets that are only resolvable against a real timestamp.
_RELATIVE_RE = re.compile(
    r"\b(?:in|within|after)\s+(\d{1,4})\s*(minute|min|hour|hr|day|week|month)s?\b"
    r"|\b(\d{1,4})\s*(minute|min|hour|hr|day|week|month)s?\s+(?:from\s+now|later|hence|ahead)\b",
    re.I,
)
_UNIT_SECONDS = {
    "minute": 60, "min": 60,
    "hour": 3600, "hr": 3600,
    "day": 86400,
    "week": 604800,
    # Months are not a fixed number of days; resolving them would be a guess,
    # so they are absent on purpose and fall through to None.
}


def _strip_wrapping(value: str) -> str:
    """Remove quoting and bracketing the model sometimes adds."""
    text = str(value or "").strip()
    # Strip matched surrounding quotes/brackets, repeatedly.
    pairs = (('"', '"'), ("'", "'"), ("`", "`"), ("[", "]"), ("(", ")"), ("{", "}"))
    changed = True
    while changed and len(text) >= 2:
        changed = False
        for open_c, close_c in pairs:
            if text[0] == open_c and text[-1] == close_c:
                text = text[1:-1].strip()
                changed = True
    return text


def _is_definitely_not_a_date(value: str) -> bool:
    if not value:
        return True
    if _FIELD_LABEL_BARE_RE.match(value):
        return True
    if _FIELD_LABEL_RE.match(value):
        return True
    if _VAGUE_RE.match(value):
        return True
    if _NON_ACTION_RE.match(value):
        return True
    return False


def _month_number(name: str) -> int | None:
    return _MONTHS.get(name.strip().lower().rstrip("."))


def _iso_from_parts(year: int, month: int, day: int) -> str | None:
    """A calendar date becomes midnight UTC, so every value has one shape."""
    try:
        return datetime(year, month, day, tzinfo=timezone.utc).isoformat()
    except ValueError:
        return None


def _resolve_calendar(text: str, reference: datetime | None) -> str | None:
    """Resolve an explicit calendar date in `text` to an ISO date."""
    # ISO datetime / date, anchored at the start.
    m = _ISO_DATETIME_RE.match(text)
    if m:
        head = m.group(0).strip()
        candidate = head.replace(" ", "T")
        if len(candidate) == 10:
            candidate += "T00:00:00+00:00"
        elif len(candidate) == 16:
            candidate += ":00+00:00"
        elif not re.search(r"(?:Z|[+-]\d{2}:?\d{2})$", candidate):
            candidate += "+00:00"
        try:
            parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed.astimezone(timezone.utc).isoformat()

    m = _ISO_DATE_RE.match(text)
    if m:
        return _iso_from_parts(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    # Drop ordinal suffixes so "12th September 2026" matches the plain pattern.
    flat = _ORDINAL_SUFFIX_RE.sub(r"\1", text)

    m = _DMY_RE.search(flat)
    if m:
        return _iso_from_parts(int(m.group(3)), _month_number(m.group(2)) or 0, int(m.group(1)))

    m = _MDY_RE.search(flat)
    if m:
        return _iso_from_parts(int(m.group(3)), _month_number(m.group(1)) or 0, int(m.group(2)))

    # A date with no year is only usable when a reference supplies the year.
    if reference is not None:
        m = _DMY_NO_YEAR_RE.search(flat)
        if m:
            month = _month_number(m.group(2))
            if month:
                return _iso_from_parts(reference.year, month, int(m.group(1)))
        m = _MDY_NO_YEAR_RE.search(flat)
        if m:
            month = _month_number(m.group(1))
            if month:
                return _iso_from_parts(reference.year, month, int(m.group(2)))

    return None


def _resolve_relative(text: str, reference: datetime | None) -> str | None:
    """Resolve "in 2 days" / "15 minutes from now" against a reference."""
    if reference is None:
        return None
    m = _RELATIVE_RE.search(text)
    if not m:
        return None
    if m.group(1) is not None:
        amount, unit = int(m.group(1)), m.group(2).lower()
    else:
        amount, unit = int(m.group(3)), m.group(4).lower()
    seconds = _UNIT_SECONDS.get(unit)
    if seconds is None:
        return None
    return (reference + timedelta(seconds=amount * seconds)).astimezone(timezone.utc).isoformat()


def normalize_due_at(raw: object, reference: datetime | None = None) -> str | None:
    """Return a normalised ISO-8601 due timestamp, or ``None``.

    ``reference`` is the source message's timestamp. It is required to resolve
    a date that omits its year and to resolve relative wording; without it
    those forms return ``None`` rather than being guessed at.
    """
    if raw is None:
        return None
    if isinstance(raw, datetime):
        return raw.astimezone(timezone.utc).isoformat()
    if isinstance(raw, date):
        return _iso_from_parts(raw.year, raw.month, raw.day)
    if not isinstance(raw, str):
        return None

    value = _strip_wrapping(raw)
    if not value:
        return None
    if _is_definitely_not_a_date(value):
        return None

    # Reject a string that carries a field label anywhere it introduces a value.
    resolved = _resolve_calendar(value, reference)
    if resolved is not None:
        return resolved
    return _resolve_relative(value, reference)


def is_temporal_only(value: object) -> bool:
    """True when `value` is nothing but a date/time expression.

    A deadline entry whose description is purely "12th September 2026" or
    "15 minutes from now" describes no action, so it must not become a task
    with that text as its title.
    """
    text = _strip_wrapping(value if isinstance(value, str) else "")
    if not text:
        return True
    if _FIELD_LABEL_RE.match(text) or _FIELD_LABEL_BARE_RE.match(text):
        return True
    if _NON_ACTION_RE.match(text):
        return True
    if _VAGUE_RE.match(text):
        return True
    if _BARE_TIME_RE.match(text):
        return True

    flat = _ORDINAL_SUFFIX_RE.sub(r"\1", text)
    # A weekday gloss in brackets adds no information, so drop it before
    # deciding whether anything but a date remains.
    flat = _WEEKDAY_GLOSS_RE.sub(" ", flat)
    # A recognised date with nothing else around it.
    if _DMY_RE.search(flat) or _MDY_RE.search(flat) or _ISO_DATE_RE.match(text.strip()):
        remainder = re.sub(
            rf"(\d{{1,2}}\s*(?:st|nd|rd|th)?\s+(?:{_MONTH_ALT})\.?\s*,?\s*\d{{4}})"
            rf"|((?:{_MONTH_ALT})\.?\s*\d{{1,2}}\s*(?:st|nd|rd|th)?\s*,?\s*\d{{4}})"
            rf"|(\d{{4}}-\d{{2}}-\d{{2}})",
            " ",
            flat,
            flags=re.I,
        )
        if not remainder.strip(" ,.-â€“â€”/()"):
            return True

    if _RELATIVE_RE.search(text):
        remainder = _RELATIVE_RE.sub(" ", text)
        if not remainder.strip(" ,.-â€“â€”/()"):
            return True
    return False


def is_non_action(value: object) -> bool:
    """True when `value` states that no action is required."""
    if not isinstance(value, str):
        return False
    text = _strip_wrapping(value)
    if not text:
        return True
    return bool(_NON_ACTION_RE.match(text))


def is_relative_expression(value: object) -> bool:
    """True when `value` is a relative offset that a timestamp can resolve.

    The extraction schema is validated without the message's timestamp, so it
    cannot turn "in 2 days" into an instant. Rather than discard a form that
    *is* deterministic once a reference exists, the schema keeps it and
    derivation resolves it against ``email.received_at``. Anything that is not
    a recognised offset ("soon", "at the earliest", a leaked field label) is
    rejected here and never survives.
    """
    if not isinstance(value, str):
        return False
    text = _strip_wrapping(value)
    if not text or _is_definitely_not_a_date(text):
        return False
    return bool(_RELATIVE_RE.search(text))

