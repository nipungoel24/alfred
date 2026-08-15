import hashlib
import json
from ..schemas import Email

BRIEFING_SCHEMA_VERSION = "1"

def briefing_fingerprint(emails: list[Email], model: str) -> str:
    """Fingerprint compact analyses, never raw email bodies."""
    compact = [{"id": email.id, "analysis": email.analysis.model_dump(mode="json")} for email in sorted(emails, key=lambda value: value.id) if email.analysis]
    payload = {"version": BRIEFING_SCHEMA_VERSION, "model": model, "emails": compact}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
