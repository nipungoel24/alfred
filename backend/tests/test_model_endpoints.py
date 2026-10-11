"""Gate 2: local-model endpoints, and the OAuth state bound fixed as D15.

The model endpoints are the only HTTP surface for criteria 2.3-2.7, so
they are tested here against a supervisor driven by a fake Ollama client
rather than a running daemon. The OAuth half covers the unbounded,
non-expiring `OAUTH_STATES` dict found in Gate 1.
"""
import time

import pytest
from fastapi.testclient import TestClient

from backend.app import main as main_mod
from backend.app.ai.supervisor import AISupervisor, AIState
from backend.app.db.repositories import Repository
from backend.tests.test_model_supervisor import FakePullClient


@pytest.fixture
def oauth_states():
    """Isolate the shared OAuth dict for the duration of one test."""
    saved = dict(main_mod.OAUTH_STATES)
    main_mod.OAUTH_STATES.clear()
    yield main_mod.OAUTH_STATES
    main_mod.OAUTH_STATES.clear()
    main_mod.OAUTH_STATES.update(saved)


@pytest.fixture
def client(monkeypatch, tmp_path):
    """One client whose portal loop outlives each request.

    A download task created by one request has to still be running when the
    next request arrives. That only holds while the portal loop is shared,
    which TestClient does when used as a context manager. Entering the
    context also runs the lifespan, so the background workers are stubbed
    and the repository is swapped for a throwaway one: the session-wide
    connection must not be closed by a test.
    """
    async def _noop():
        return None

    for name in (
        "_analysis_worker", "_backfill_worker", "_label_backfill",
        "_backfill_estimate_once", "_startup_background",
    ):
        monkeypatch.setattr(main_mod, name, _noop)

    monkeypatch.setattr(
        main_mod, "repo", Repository(tmp_path / "gate2_endpoints.db")
    )

    with TestClient(main_mod.app) as c:
        yield c


def _wire(monkeypatch, pull_client=None):
    """Point the app's module singletons at fakes and return the supervisor."""
    pull_client = pull_client or FakePullClient()
    supervisor = AISupervisor(pull_client, "qwen3:4b")
    monkeypatch.setattr(main_mod, "ai_supervisor", supervisor)
    monkeypatch.setattr(main_mod, "ollama_client", pull_client)
    monkeypatch.setattr(main_mod.settings, "ollama_model", "qwen3:4b")
    monkeypatch.setattr(main_mod.ai, "model", "qwen3:4b")
    return supervisor, pull_client


def _state(client):
    return client.get("/api/analysis/status").json()


def _await_pull(client, sup, timeout=5.0):
    """Wait for a download to settle, without touching its event loop.

    `start_pull` runs inside TestClient's portal loop, so its task cannot
    be awaited from the test thread with `asyncio.run`. The portal loop is
    alive in the background, so polling the status endpoint (which yields
    the loop between requests) lets the task finish on its own loop.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not sup.pulling:
            return _state(client)
        time.sleep(0.02)
    raise AssertionError("download did not settle within the timeout")


# ── D15: the OAuth state dict is bounded and expires ──

def test_a_denied_callback_releases_its_state_immediately(oauth_states, client):
    # Before the fix a denied flow never popped its entry, so declining
    # the consent screen leaked one permanent dict key.
    oauth_states["st1"] = {
        "verifier": "v", "redirect_uri": "http://x", "created_at": time.time(),
    }
    r = client.get(
        "/api/accounts/gmail/callback",
        params={"error": "access_denied", "state": "st1"},
    )
    assert r.status_code == 400
    assert "st1" not in oauth_states


def test_an_abandoned_state_is_purged_once_the_ttl_passes(oauth_states):
    oauth_states["stale"] = {
        "verifier": "v", "redirect_uri": "http://x",
        "created_at": time.time() - (main_mod.OAUTH_STATE_TTL_SECONDS + 1),
    }
    oauth_states["fresh"] = {
        "verifier": "v", "redirect_uri": "http://x", "created_at": time.time(),
    }
    main_mod._purge_expired_oauth_states()
    assert "stale" not in oauth_states
    assert "fresh" in oauth_states


def test_an_expired_state_is_rejected_even_before_a_purge_runs(oauth_states, client):
    # The purge runs on the next connect, so redemption has to check the
    # age itself or a state could be redeemed long after it should count.
    oauth_states["stale"] = {
        "verifier": "v", "redirect_uri": "http://x",
        "created_at": time.time() - (main_mod.OAUTH_STATE_TTL_SECONDS + 1),
    }
    r = client.get(
        "/api/accounts/gmail/callback", params={"code": "c", "state": "stale"},
    )
    assert r.status_code == 400
    assert "stale" not in oauth_states


def test_the_state_dict_never_exceeds_its_cap(oauth_states):
    # A hostile client that spams /connect could grow this without bound.
    total = main_mod.OAUTH_STATE_MAX + 20
    for i in range(total):
        main_mod._register_oauth_state(f"s{i}", f"v{i}", "http://x")

    assert len(oauth_states) == main_mod.OAUTH_STATE_MAX
    # The oldest entries were dropped; the newest survived.
    assert "s0" not in oauth_states
    assert f"s{total - 1}" in oauth_states


def test_cap_eviction_drops_the_oldest_not_an_arbitrary_flow(oauth_states):
    base = time.time() - 100
    for i in range(main_mod.OAUTH_STATE_MAX):
        oauth_states[f"s{i}"] = {
            "verifier": "v", "redirect_uri": "http://x", "created_at": base + i,
        }
    main_mod._register_oauth_state("newest", "v", "http://x")
    assert "newest" in oauth_states
    assert "s0" not in oauth_states          # oldest went
    assert f"s{main_mod.OAUTH_STATE_MAX - 1}" in oauth_states  # newest kept


def test_purging_keeps_concurrent_recent_flows_alive(oauth_states):
    # Several flows started moments apart are all legitimate; the TTL
    # must not treat one as dead while another is still being finished.
    now = time.time()
    for i in range(4):
        oauth_states[f"live{i}"] = {
            "verifier": "v", "redirect_uri": "http://x", "created_at": now - i,
        }
    main_mod._purge_expired_oauth_states()
    assert len(oauth_states) == 4


# ── Criterion 2.3 / 2.5 / 2.6: model status and preflight ──

def test_model_status_reports_a_real_size_and_a_real_disk_free(client, monkeypatch):
    sup, pull_client = _wire(monkeypatch)
    pull_client.models = ["qwen3:4b"]
    pull_client.model_sizes = {"qwen3:4b": 4000000000}

    body = client.get("/api/ai/model").json()

    assert body["model"] == "qwen3:4b"
    # The size is Ollama's own figure for what is on disk, not a constant.
    assert body["size_bytes"] == 4000000000
    # human_bytes uses binary steps, so 4e9 bytes is 3.7 GB.
    assert body["human_size"] == "3.7 GB"
    assert body["local_models"][0]["name"] == "qwen3:4b"
    assert body["local_models"][0]["size_bytes"] == 4000000000
    # Disk figures come from this machine.
    assert body["preflight"]["disk_free_bytes"] > 0
    assert body["preflight"]["disk_path"]


def test_model_status_survives_an_offline_ollama(client, monkeypatch):
    class Offline:
        async def list_models(self):
            from backend.app.ai.ollama_client import OllamaUnavailable
            raise OllamaUnavailable("offline")
        async def model_size(self, model):
            return None

    monkeypatch.setattr(main_mod, "ollama_client", Offline())
    r = client.get("/api/ai/model")
    assert r.status_code == 200
    body = r.json()
    assert body["local_models"] == []
    assert body["size_bytes"] is None
    # An unknown size is named as unknown, never filled in with a guess.
    assert body["human_size"] == "unknown size"


def test_model_status_populates_the_preflight_from_this_machine(client, monkeypatch):
    # An uninstalled model has no knowable size, so the preflight must
    # not invent one; it reports the machine's real free space and RAM.
    sup, pull_client = _wire(monkeypatch)
    pull_client.models = []

    body = client.get("/api/ai/model").json()
    assert body["size_bytes"] is None
    assert body["human_size"] == "unknown size"
    pre = body["preflight"]
    assert pre["disk_free_bytes"] > 0
    assert pre["ram_bytes"] is None or pre["ram_bytes"] > 0
    # Unknown size can never be judged insufficient, so this is not blocking.
    assert pre["blocking"] is False
    assert pre["code"] is None


# ── Criterion 2.7: model selection ──

def test_selecting_a_model_re_runs_the_readiness_check(client, monkeypatch):
    sup, _ = _wire(monkeypatch)
    r = client.post("/api/ai/model", json={"model": "llama3.2:3b"})
    assert r.status_code == 200
    # The new target is not installed by the fake, so the honest state
    # is model_missing, not a stale ready.
    assert r.json()["state"] == AIState.MODEL_MISSING
    assert sup.model == "llama3.2:3b"
    assert main_mod.settings.ollama_model == "llama3.2:3b"
    assert main_mod.ai.model == "llama3.2:3b"
    assert client.get("/api/config").json()["ollama_model"] == "llama3.2:3b"


def test_pulling_a_new_model_synchronizes_settings_and_service(client, monkeypatch):
    sup, pull_client = _wire(monkeypatch)
    pull_client.steps = 1
    pull_client.pull_behaviour = "hang"

    r = client.post("/api/ai/model/pull", json={"model": "llama3.2:1b"})
    assert r.status_code == 200
    assert sup.model == "llama3.2:1b"
    assert main_mod.settings.ollama_model == "llama3.2:1b"
    assert main_mod.ai.model == "llama3.2:1b"
    assert client.get("/api/config").json()["ollama_model"] == "llama3.2:1b"

    pull_client.release = True


def test_selecting_an_empty_model_is_rejected(client, monkeypatch):
    _wire(monkeypatch)
    r = client.post("/api/ai/model", json={"model": ""})
    assert r.status_code == 422


def test_the_model_cannot_be_changed_while_a_download_runs(client, monkeypatch):
    sup, pull_client = _wire(monkeypatch)
    pull_client.steps = 1          # stop after one progress step
    pull_client.pull_behaviour = "hang"

    r = client.post("/api/ai/model/pull", json={})
    assert r.status_code == 200
    assert sup.pulling is True

    r = client.post("/api/ai/model", json={"model": "llama3.2:3b"})
    assert r.status_code == 409
    assert sup.model == "qwen3:4b"  # unchanged

    pull_client.release = True      # let the task end cleanly


# ── Criterion 2.4: download, progress, cancellation ──

def test_pull_returns_live_progress_on_the_status_endpoint(client, monkeypatch):
    sup, pull_client = _wire(monkeypatch)
    pull_client.models = ["qwen3:4b"]
    # Hold the download open so progress can be observed mid-flight; a
    # finished download deliberately clears its progress.
    pull_client.steps = 2
    pull_client.pull_behaviour = "hang"

    r = client.post("/api/ai/model/pull", json={})
    assert r.status_code == 200
    assert r.json()["state"] == AIState.MODEL_DOWNLOADING

    status = _state(client)
    assert status["pull"] is not None
    assert status["pull"]["running"] is True
    assert status["pull"]["status"].startswith("pulling")
    assert status["pull"]["total_bytes"] == 1000
    # Real byte counts off the stream, not a timer or a constant.
    assert status["pull"]["completed_bytes"] == 500

    # Release it; a finished download is not readiness on its own, so the
    # smoke test has to run before the state can become ready.
    pull_client.release = True
    final = _await_pull(client, sup)
    assert final["state"] == AIState.READY
    # Completed downloads must not leave a stale progress bar behind.
    assert final["pull"] is None


def test_pull_is_idempotent_while_running(client, monkeypatch):
    sup, pull_client = _wire(monkeypatch)
    pull_client.steps = 1
    pull_client.pull_behaviour = "hang"

    first = client.post("/api/ai/model/pull", json={}).json()
    second = client.post("/api/ai/model/pull", json={}).json()
    assert first["state"] == AIState.MODEL_DOWNLOADING
    assert second["state"] == AIState.MODEL_DOWNLOADING
    assert pull_client.pull_calls == 1, "a duplicate download must not start"

    pull_client.release = True


def test_cancelling_a_download_is_idempotent(client, monkeypatch):
    sup, pull_client = _wire(monkeypatch)
    pull_client.steps = 1
    pull_client.pull_behaviour = "hang"

    client.post("/api/ai/model/pull", json={})
    # Cancelling when nothing is running must not raise either.
    client.post("/api/ai/model/cancel", json={})
    r = client.post("/api/ai/model/cancel", json={})
    assert r.status_code == 200
    assert sup.pulling is False
    assert _state(client)["pull"] is None


def test_a_pull_that_will_not_fit_the_disk_fails_with_a_real_shortfall(client, monkeypatch):
    sup, pull_client = _wire(monkeypatch)
    pull_client.pull_behaviour = "space"

    client.post("/api/ai/model/pull", json={})

    status = _await_pull(client, sup)
    assert status["state"] == AIState.MODEL_FAILED
    assert status["pull"]["code"] == "INSUFFICIENT_DISK_SPACE"
