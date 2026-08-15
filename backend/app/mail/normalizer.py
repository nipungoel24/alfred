import re
from datetime import datetime
from html import unescape
from ..schemas import Email

def normalize_text(value: object) -> str:
    text = unescape(str(value or "")).replace("\\n", "\n")
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"[ \t]+", " ", text).strip()

def normalized_email(row: dict, index: int) -> Email:
    key = lambda *names: next((row.get(n) for n in names if row.get(n) not in (None, "")), None)
    raw_date = key("timestamp", "received_at", "date")
    try: received = datetime.fromisoformat(str(raw_date).replace("Z", "+00:00")) if raw_date else None
    except ValueError: received = None
    sender = normalize_text(key("sender_email", "sender", "from")) or "unknown@local"
    return Email(id=normalize_text(key("email_id", "id")) or f"import-{index}", thread_id=normalize_text(key("thread_id")) or None,
        sender=sender, sender_name=normalize_text(key("sender_name", "from_name")) or None, subject=normalize_text(key("subject")) or "(No subject)",
        body=normalize_text(key("body", "content", "message")) or "(No content)", received_at=received,
        source_metadata={"has_attachment": str(key("has_attachment") or "").lower() in {"true","1","yes"}})
