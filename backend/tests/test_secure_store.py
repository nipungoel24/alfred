"""Credential storage contract.

Alfred must never hold a Google credential in a form it cannot protect. These
tests pin that contract, including the fail-closed path that a previous
version silently violated.
"""
import base64
import sys

import pytest

from backend.app.db import secure_store
from backend.app.db.secure_store import (
    FORMAT_VERSION,
    SecureStoreUnavailable,
    decrypt_token,
    encrypt_token,
    is_available,
    status,
)

pytestmark = pytest.mark.skipif(
    sys.platform != "win32", reason="Windows DPAPI is the supported store"
)


class TestRealDpapiIsActuallyUsed:
    def test_availability_probe_succeeds_on_windows(self):
        assert is_available() is True
        assert status() == "ready"

    def test_round_trip_returns_the_original_secret(self):
        secret = "ya29.a0AfB_byThisIsATest_refresh-token_value"
        blob = encrypt_token(secret)
        assert decrypt_token(blob) == secret

    def test_stored_blob_is_not_reversible_base64(self):
        # The regression this whole module exists to prevent: a credential
        # that can be recovered with base64 alone is plaintext.
        secret = "1//0gRefreshTokenThatLooksLikeBase64Padding"
        blob = encrypt_token(secret)
        with pytest.raises(Exception):
            base64.b64decode(bytes(blob), validate=True)

    def test_stored_blob_carries_the_format_version(self):
        blob = encrypt_token("token")
        assert blob[:1] == FORMAT_VERSION

    def test_ciphertext_does_not_contain_the_plaintext(self):
        secret = "super-secret-refresh-token"
        blob = encrypt_token(secret)
        assert secret.encode() not in bytes(blob)

    def test_two_encryptions_of_the_same_value_differ(self):
        # DPAPI salts every blob, so identical inputs must not produce
        # identical ciphertext.
        a = encrypt_token("same-value")
        b = encrypt_token("same-value")
        assert a != b
        assert decrypt_token(a) == decrypt_token(b) == "same-value"

    def test_empty_secret_round_trips_to_empty(self):
        assert encrypt_token("") == b""
        assert decrypt_token(b"") == ""


class TestFailClosed:
    """When DPAPI cannot protect a credential, Alfred must refuse."""

    def test_encrypt_raises_when_the_store_is_unavailable(self, monkeypatch):
        monkeypatch.setattr(secure_store, "_FORCE_UNAVAILABLE", True)
        with pytest.raises(SecureStoreUnavailable) as exc:
            encrypt_token("a-real-refresh-token")
        message = str(exc.value)
        assert "reversible" in message
        assert "a-real-refresh-token" not in message, "must not echo the secret"

    def test_no_credential_is_returned_when_storage_fails(self, monkeypatch):
        monkeypatch.setattr(secure_store, "_FORCE_UNAVAILABLE", True)
        with pytest.raises(SecureStoreUnavailable):
            encrypt_token("a-real-refresh-token")

    def test_status_reports_unavailable_when_dpapi_is_missing(self, monkeypatch):
        monkeypatch.setattr(secure_store, "_FORCE_UNAVAILABLE", True)
        assert is_available() is False
        assert status() == "unavailable"

    def test_a_dpapi_encrypt_failure_raises_rather_than_downgrading(
        self, monkeypatch
    ):
        def boom(_data):
            raise OSError("CryptProtectData failed")

        monkeypatch.setattr(secure_store, "is_available", lambda: True)
        monkeypatch.setattr(secure_store, "_win_encrypt", boom)
        with pytest.raises(SecureStoreUnavailable):
            encrypt_token("a-real-refresh-token")

    def test_a_dpapi_decrypt_failure_raises_rather_than_returning_empty(
        self, monkeypatch
    ):
        blob = encrypt_token("token")
        monkeypatch.setattr(secure_store, "_win_decrypt", lambda _b: (_ for _ in ()).throw(OSError("no")))
        with pytest.raises(SecureStoreUnavailable):
            decrypt_token(blob)

    def test_a_corrupt_versioned_blob_raises(self):
        with pytest.raises(SecureStoreUnavailable):
            decrypt_token(FORMAT_VERSION + b"not-real-dpapi-ciphertext")


class TestLegacyMigration:
    """Rows written by the pre-versioning build must remain readable."""

    def test_legacy_base64_value_is_still_readable(self):
        legacy = base64.b64encode(b"legacy-refresh-token")
        assert decrypt_token(legacy) == "legacy-refresh-token"

    def test_legacy_value_is_flagged_as_a_security_event(self, caplog):
        legacy = base64.b64encode(b"legacy-refresh-token")
        with caplog.at_level("WARNING", logger="alfred.secure_store"):
            decrypt_token(legacy)
        assert any(
            "legacy_unprotected_credential_detected" in r.message
            or "legacy_unprotected_credential_detected" in r.getMessage()
            for r in caplog.records
        )

    def test_a_versioned_blob_is_not_treated_as_legacy(self, caplog):
        caplog.clear()
        blob = encrypt_token("token")
        with caplog.at_level("WARNING", logger="alfred.secure_store"):
            decrypt_token(blob)
        assert not any(
            "legacy_unprotected_credential_detected" in r.getMessage()
            for r in caplog.records
        )

    def test_unreadable_legacy_value_raises(self):
        with pytest.raises(SecureStoreUnavailable):
            decrypt_token(b"!!! not base64 !!!")

    def test_a_legacy_value_can_be_re_encrypted(self):
        legacy = base64.b64encode(b"legacy-refresh-token")
        recovered = decrypt_token(legacy)
        upgraded = encrypt_token(recovered)
        assert upgraded[:1] == FORMAT_VERSION
        assert decrypt_token(upgraded) == "legacy-refresh-token"


class TestHealthReporting:
    def test_health_reports_a_single_known_state(self):
        assert status() in {"ready", "unavailable"}
