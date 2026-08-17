"""Persisted progressive All Mail backfill state.

The sync_cursor JSON of a Gmail account carries a typed backfill block:

    backfill_state            not_started | running | paused | complete | failed
    backfill_page_token       Gmail page token for the next bounded page
    backfill_estimate         resultSizeEstimate from Gmail (approximate)
    backfill_imported         messages imported by the backfill so far
    backfill_pages            bounded pages processed so far
    backfill_last_page_at     ISO timestamp of the last successful page
    backfill_last_error       sanitized error code/message (no secrets)

Legacy cursors (backfill_complete / backfill_page_token only) are
normalized into the typed model on read. The frontend OBSERVES this state;
the backend job system owns it.
"""
import json
from datetime import datetime, timezone

from .eligibility import BackfillState

VALID_STATES = {s.value for s in BackfillState}

BACKFILL_CURSOR_FIELDS = (
    "backfill_state",
    "backfill_page_token",
    "backfill_estimate",
    "backfill_imported",
    "backfill_pages",
    "backfill_last_page_at",
    "backfill_last_error",
)


def normalize_cursor(sync_cursor: str | None) -> dict:
    """Parse a sync cursor and normalize its backfill block."""
    try:
        data = json.loads(sync_cursor) if sync_cursor else {}
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}

    state = data.get("backfill_state")
    if state not in VALID_STATES:
        # Legacy migration
        if data.get("backfill_complete"):
            state = BackfillState.COMPLETE.value
        elif data.get("backfill_page_token"):
            state = BackfillState.RUNNING.value
        else:
            state = BackfillState.NOT_STARTED.value
        data["backfill_state"] = state

    data.setdefault("backfill_page_token", None)
    data.setdefault("backfill_estimate", None)
    data.setdefault("backfill_imported", 0)
    data.setdefault("backfill_pages", 0)
    data.setdefault("backfill_last_page_at", None)
    data.setdefault("backfill_last_error", None)
    return data


def dump_cursor(data: dict) -> str:
    return json.dumps(data)


def set_state(data: dict, state: BackfillState) -> dict:
    data["backfill_state"] = state.value
    if state == BackfillState.COMPLETE:
        data["backfill_page_token"] = None
    return data


def record_success(data: dict, imported: int, page_token: str | None,
                   estimate: int | None) -> dict:
    """Update counters after one successful bounded page."""
    data["backfill_imported"] = int(data.get("backfill_imported") or 0) + int(imported or 0)
    data["backfill_pages"] = int(data.get("backfill_pages") or 0) + 1
    data["backfill_page_token"] = page_token
    if estimate is not None:
        data["backfill_estimate"] = int(estimate)
    data["backfill_last_page_at"] = datetime.now(timezone.utc).isoformat()
    data["backfill_last_error"] = None
    return data


def record_failure(data: dict, error_code: str, error_message: str) -> dict:
    data["backfill_last_error"] = f"{error_code}: {error_message[:200]}"
    return data


def status_payload(data: dict) -> dict:
    """Observer-facing backfill status (no tokens, no secrets)."""
    estimate = data.get("backfill_estimate")
    imported = int(data.get("backfill_imported") or 0)
    remaining = None
    if estimate is not None:
        remaining = max(0, estimate - imported)
    return {
        "state": data.get("backfill_state"),
        "complete": data.get("backfill_state") == BackfillState.COMPLETE.value,
        "estimate": estimate,
        "imported": imported,
        "pages": int(data.get("backfill_pages") or 0),
        "remaining_estimate": remaining,
        "last_page_at": data.get("backfill_last_page_at"),
        "last_error": data.get("backfill_last_error"),
    }
