"""Canonical account-scoped email identity for Alfred.

Two distinct concepts:

- provider message ID: Gmail's raw message id (hex, e.g. "1a076e26cf3a3533").
  Only ever sent to the provider's API, never used as a global Alfred key.
- local scoped ID: Alfred's database identity for a stored email,
  "gmail_{account_id}_{provider_message_id}". Globally unique per account,
  so two Gmail accounts that both hold a message with the SAME provider id
  never collide.

Threads follow the SAME rule: provider thread IDs are NOT globally unique
(they are only unique inside one Gmail mailbox), so Alfred stores a scoped
local thread ID "gmail_{account_id}_{provider_thread_id}" and keeps the
raw provider thread id in source_metadata.gmail_raw.threadId. Draft
context, task linkage and thread queries always use the scoped form —
cross-account thread content must never enter an AI prompt (privacy
boundary).

INVARIANT (pinned by tests):
- Email.id is always the scoped local id for provider mail.
- Email.thread_id is always the scoped local thread id for provider mail.
- (account_id, provider_message_id) is UNIQUE (partial unique index;
  legacy CSV rows carry NULLs and are exempt).
- Parsing a scoped id NEVER depends on provider formatting EXCEPT as a
  legacy fallback: exact-prefix matching against the known account id is
  authoritative. The trailing-hex regex only interprets ids whose account
  is unknown (e.g. migration of pre-scoping databases), and Gmail provider
  ids are hex in practice. See P1-3 notes in database.py.
"""

import re

SCOPE_PREFIX = "gmail"

# provider message ids are hex-only (Gmail ids are [0-9a-f]{10,});
# account ids may legally contain underscores (local-part of an email),
# so parse by anchoring the trailing hex run.
_SCOPED_RE = re.compile(r"^gmail_(.+)_([0-9a-f]{10,})$")


def scoped_email_id(account_id: str, provider_message_id: str) -> str:
    """Build the local scoped identity for a provider message."""
    if not account_id:
        return provider_message_id
    return f"{SCOPE_PREFIX}_{account_id}_{provider_message_id}"


def parse_email_id(email_id: str) -> tuple[str | None, str | None]:
    """Split a scoped local id into (account_id, provider_message_id).

    Returns (None, None) when the id is not scoped (e.g. legacy raw ids
    or CSV imports).
    """
    if not email_id:
        return None, None
    match = _SCOPED_RE.match(email_id)
    if not match:
        return None, None
    return match.group(1), match.group(2)


def provider_message_id(email_id: str) -> str | None:
    """The provider-side message id for a local id, or None if not scoped."""
    return parse_email_id(email_id)[1]


def is_scoped_for(email_id: str, account_id: str) -> bool:
    """True when the local id was generated for the given account.

    Authoritative check: exact prefix match against the KNOWN account id.
    Never depends on provider-id formatting.
    """
    if not email_id or not account_id:
        return False
    prefix = f"{SCOPE_PREFIX}_{account_id}_"
    if email_id.startswith(prefix) and len(email_id) > len(prefix):
        return True
    # Legacy fallback: regex parse agrees on the account.
    parsed_account, _ = parse_email_id(email_id)
    return parsed_account == account_id


def scoped_thread_id(account_id: str, provider_thread_id: str | None) -> str | None:
    """Build the local scoped identity for a provider thread."""
    if not provider_thread_id:
        return None
    if not account_id:
        return provider_thread_id
    return f"{SCOPE_PREFIX}_{account_id}_{provider_thread_id}"


def parse_thread_id(thread_id: str | None) -> tuple[str | None, str | None]:
    """Split a scoped local thread id into (account_id, provider_thread_id)."""
    return parse_email_id(thread_id or "")


def strip_scope(scoped_id: str, account_id: str) -> str:
    """Remove a known account prefix, returning the provider-side id.

    Raises ValueError when the id is not scoped for that account — callers
    must never silently send a local id to a provider API.
    """
    prefix = f"{SCOPE_PREFIX}_{account_id}_"
    if scoped_id.startswith(prefix) and len(scoped_id) > len(prefix):
        return scoped_id[len(prefix):]
    raise ValueError(f"local id is not scoped for account {account_id!r}")
