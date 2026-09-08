"""Canonical account-scoped email identity for Alfred.

Two distinct concepts:

- provider message ID: Gmail's raw message id (hex, e.g. "1a076e26cf3a3533").
  Only ever sent to the provider's API, never used as a global Alfred key.
- local scoped ID: Alfred's database identity for a stored email,
  "gmail_{account_id}_{provider_message_id}". Globally unique per account,
  so two Gmail accounts that both hold a message with the SAME provider id
  never collide.

All scoped ID construction/parsing MUST go through this module — never
ad-hoc f-string prefixes in random functions.
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
    """True when the local id was generated for the given account."""
    parsed_account, _ = parse_email_id(email_id)
    return parsed_account == account_id
