"""Windows DPAPI credential storage for Alfred.

Security contract
-----------------
1. Credentials are encrypted with Windows DPAPI (``CryptProtectData``), bound
   to the current user account and machine.
2. Storage is **fail-closed**. If DPAPI is unavailable or fails, Alfred raises
   :class:`SecureStoreUnavailable`. It never falls back to a reversible
   encoding. A previous version silently fell back to ``base64``, which is
   plaintext with extra steps and produced no signal that it had done so.
3. Every stored blob carries a one-byte format version so a reader can tell
   DPAPI ciphertext from a legacy unversioned value with certainty, instead of
   trying each decoder in turn.

Legacy migration
----------------
Installations created before versioning stored unversioned base64. Those rows
are still readable, but reading one is treated as a security event: the value
is re-encrypted with DPAPI and written back by the caller, and a warning is
logged. Alfred upgrades its own credentials rather than stranding a user who
would otherwise have to reconnect every account.

History
-------
The DPAPI path was broken on Python 3.12 and newer: the ``DATA_BLOB``
structure used ``ctypes.BYTE``, which was removed from the standard library.
Every encrypt and decrypt call raised ``AttributeError``, and the old
``except Exception: pass`` fallback swallowed it and stored base64 instead.
Credentials written by an affected build are therefore reversible and should
be treated as compromised. Fail-closed behaviour is what surfaced this; a
silent fallback hid it.
"""
from __future__ import annotations

import base64
import binascii
import logging
import sys

logger = logging.getLogger("alfred.secure_store")

#: Format version stored as the first byte of every blob written by this
#: module. Bump only if the ciphertext layout changes.
FORMAT_VERSION = b"\x01"

#: Test hook: forces the DPAPI path to appear unavailable so the fail-closed
#: behaviour can be exercised on any platform.
_FORCE_UNAVAILABLE = False


class SecureStoreUnavailable(RuntimeError):
    """Raised when a credential cannot be protected or unprotected.

    This is deliberately fatal to the caller. Alfred must not proceed to store
    a Google refresh token in any form it cannot protect.
    """


def _win_encrypt(data: bytes) -> bytes:
    import ctypes
    from ctypes import wintypes

    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]

    in_blob = DATA_BLOB(
        len(data),
        ctypes.cast(ctypes.create_string_buffer(data), ctypes.POINTER(ctypes.c_ubyte)),
    )
    out_blob = DATA_BLOB()
    # Flags = 0: bind to the current user, not the machine. No optional
    # entropy, so the blob depends only on the DPAPI master keys.
    res = crypt32.CryptProtectData(
        ctypes.byref(in_blob), None, None, None, None, 0, ctypes.byref(out_blob)
    )
    if not res:
        raise OSError(f"CryptProtectData failed (winerror={kernel32.GetLastError()})")
    try:
        return ctypes.string_at(out_blob.pbData, out_blob.cbData)
    finally:
        kernel32.LocalFree(out_blob.pbData)


def _win_decrypt(enc_data: bytes) -> bytes:
    import ctypes
    from ctypes import wintypes

    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]

    in_blob = DATA_BLOB(
        len(enc_data),
        ctypes.cast(ctypes.create_string_buffer(enc_data), ctypes.POINTER(ctypes.c_ubyte)),
    )
    out_blob = DATA_BLOB()
    res = crypt32.CryptUnprotectData(
        ctypes.byref(in_blob), None, None, None, None, 0, ctypes.byref(out_blob)
    )
    if not res:
        raise OSError(f"CryptUnprotectData failed (winerror={kernel32.GetLastError()})")
    try:
        return ctypes.string_at(out_blob.pbData, out_blob.cbData)
    finally:
        kernel32.LocalFree(out_blob.pbData)


def is_available() -> bool:
    """True when a credential can be protected on this machine right now."""
    if _FORCE_UNAVAILABLE:
        return False
    if sys.platform != "win32":
        return False
    try:
        _win_encrypt(b"alfred-probe")
    except Exception as exc:  # noqa: BLE001 - probe must never raise
        logger.error("secure_store.probe_failed error=%s", type(exc).__name__)
        return False
    return True


def status() -> str:
    """A single word describing the credential store, for `/health`."""
    return "ready" if is_available() else "unavailable"


def encrypt_token(token: str) -> bytes:
    """Encrypt a credential for storage.

    Raises:
        SecureStoreUnavailable: if the credential cannot be protected. Alfred
            must not continue; storing it any other way would be worse.
    """
    if not token:
        return b""
    if not is_available():
        raise SecureStoreUnavailable(
            "Windows DPAPI is unavailable, so the credential cannot be stored "
            "safely. Alfred will not store it in a reversible form."
        )
    data_bytes = token.encode("utf-8")
    try:
        ciphertext = _win_encrypt(data_bytes)
    except Exception as exc:  # noqa: BLE001 - normalised into one typed error
        logger.error("secure_store.encrypt_failed error=%s", type(exc).__name__)
        raise SecureStoreUnavailable(
            f"Windows DPAPI refused to protect the credential ({type(exc).__name__})."
        ) from exc
    return FORMAT_VERSION + ciphertext


def _looks_like_dpapi(blob: bytes) -> bool:
    """A DPAPI blob always begins with a versioned header byte."""
    return blob[:1] == FORMAT_VERSION


def decrypt_token(enc_data: bytes) -> str:
    """Decrypt a stored credential.

    Returns:
        The plaintext credential.

    Raises:
        SecureStoreUnavailable: if the value cannot be unprotected. Returning
            an empty string here would silently disconnect the user's account
            with no explanation.
    """
    if not enc_data:
        return ""
    if isinstance(enc_data, str):
        enc_data = enc_data.encode("utf-8")

    if _looks_like_dpapi(enc_data):
        ciphertext = enc_data[1:]
        try:
            return _win_decrypt(ciphertext).decode("utf-8")
        except Exception as exc:  # noqa: BLE001
            logger.error("secure_store.decrypt_failed error=%s", type(exc).__name__)
            raise SecureStoreUnavailable(
                "A stored credential could not be decrypted. The Windows user "
                "profile that encrypted it is no longer available."
            ) from exc

    # Legacy unversioned value. These were written by an older Alfred as raw
    # base64. Reading one is expected during an upgrade, so it is supported,
    # but it is logged as a security event because the value was, and remains,
    # only as protected as base64.
    logger.warning(
        "secure_store.legacy_unprotected_credential_detected "
        "action=re-encrypt_on_next_save"
    )
    try:
        return base64.b64decode(enc_data, validate=True).decode("utf-8")
    except (binascii.Error, ValueError, UnicodeDecodeError) as exc:
        raise SecureStoreUnavailable(
            "A stored credential is in an unrecognised format and cannot be read."
        ) from exc
