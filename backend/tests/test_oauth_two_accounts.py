"""OAuth account lifecycle: reconnect idempotency + second account.

Covers P1-2: the account chooser (select_account consent) is asserted in
test_gmail_mock; here the callback path proves reconnecting the SAME
Google identity updates one row (idempotent) while a DIFFERENT identity
creates a separate account row. PKCE/state validation untouched.
"""
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def isolated_app(tmp_path, monkeypatch):
    monkeypatch.setenv("ALFRED_RUNTIME_TOKEN", "test-secret-token-123")
    monkeypatch.setenv("ALFRED_DATABASE_PATH", str(tmp_path / "oauth.db"))
    import importlib
    from backend.app import config as config_mod
    from backend.app import main as main_mod
    importlib.reload(config_mod)
    importlib.reload(main_mod)
    yield main_mod.app, main_mod
    monkeypatch.delenv("ALFRED_RUNTIME_TOKEN")
    monkeypatch.delenv("ALFRED_DATABASE_PATH")
    importlib.reload(config_mod)
    importlib.reload(main_mod)


def _complete_callback(client, main_mod, email: str, name: str):
    """Drive the OAuth callback with a mocked Google side."""
    main_mod.gmail_provider.exchange_code = AsyncMock(return_value={
        "access_token": f"access-{email}",
        "refresh_token": f"refresh-{email}",
        "expires_in": 3600,
    })
    main_mod.gmail_provider.get_user_info = AsyncMock(return_value={
        "email": email, "name": name,
    })
    state = "state-for-" + email
    main_mod.OAUTH_STATES[state] = {
        "verifier": "verifier", "redirect_uri": "http://localhost/callback",
    }
    try:
        r = client.get(
            "/api/accounts/gmail/callback",
            params={"code": "code-" + email, "state": state},
        )
        assert r.status_code == 200
    finally:
        import importlib
        importlib.reload(main_mod)


def test_reconnect_same_account_is_idempotent(isolated_app):
    app, main_mod = isolated_app
    client = TestClient(app)

    _complete_callback(client, main_mod, "alice@example.com", "Alice")
    _complete_callback(client, main_mod, "alice@example.com", "Alice")

    accounts = main_mod.repo.accounts()
    assert [a.id for a in accounts] == ["gmail_alice@example.com"]


def test_second_google_identity_creates_separate_row(isolated_app):
    app, main_mod = isolated_app
    client = TestClient(app)

    _complete_callback(client, main_mod, "alice@example.com", "Alice")
    _complete_callback(client, main_mod, "bob@example.com", "Bob")

    accounts = main_mod.repo.accounts()
    ids = {a.id for a in accounts}
    assert ids == {"gmail_alice@example.com", "gmail_bob@example.com"}
    by_id = {a.id: a for a in accounts}
    assert by_id["gmail_alice@example.com"].connection_status == "connected"
    assert by_id["gmail_bob@example.com"].connection_status == "connected"
    # Separate credential rows per account.
    assert main_mod.repo.credentials("gmail_alice@example.com") is not None
    assert main_mod.repo.credentials("gmail_bob@example.com") is not None
