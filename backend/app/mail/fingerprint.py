import hashlib
from .normalizer import normalize_text
from ..schemas import Email
def content_fingerprint(email: Email) -> str:
    payload = "\x1f".join([email.sender.lower(), normalize_text(email.subject).lower(), normalize_text(email.body).lower(), email.received_at.isoformat() if email.received_at else ""])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
