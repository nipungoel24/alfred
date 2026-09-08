"""Tests for the AI supervisor state machine and queue-pause discipline.

All tests use a fake Ollama client — no network, no real model, and
absolutely no user email content.
"""
import asyncio
from pathlib import Path

import pytest

from backend.app.ai.ollama_client import (
    OllamaClient, OllamaModelMissing, OllamaTimeout, OllamaUnavailable,
)
from backend.app.ai.supervisor import AISupervisor, AIState, find_ollama_executable


class FakeClient:
    """Scriptable stand-in for OllamaClient."""

    def __init__(self):
        self.reachable = False
        self.models: list[str] = []
        self.smoke_ok = True
        self.smoke_calls = 0
        self.health_calls = 0

    async def health(self) -> dict:
        self.health_calls += 1
        if not self.reachable:
            raise OllamaUnavailable("not reachable")
        return {"models": [{"name": m} for m in self.models]}

    async def generate(self, model, prompt, schema=None, temperature=0.0):
        self.smoke_calls += 1
        if not self.reachable:
            raise OllamaUnavailable("not reachable")
        if not self.smoke_ok:
            raise OllamaTimeout("smoke timed out")
        return "ok", None


def make_supervisor(monkeypatch=None) -> tuple[AISupervisor, FakeClient]:
    client = FakeClient()
    supervisor = AISupervisor(client, "qwen3:4b")  # type: ignore[arg-type]
    if monkeypatch:
        # Auto-start must never really run in tests.
        monkeypatch.setattr(supervisor, "_try_auto_start",
                            _noop_auto_start)
        monkeypatch.setattr(supervisor, "_auto_start_attempted", True)
    return supervisor, client


async def _noop_auto_start():
    return None


def run(coro):
    return asyncio.run(coro)


def test_ollama_not_running_state(monkeypatch):
    """Unreachable server → ollama_not_running, queue paused."""
    supervisor, client = make_supervisor(monkeypatch)
    client.reachable = False

    payload = run(supervisor.refresh(allow_auto_start=False))

    assert payload["state"] == AIState.OLLAMA_NOT_RUNNING
    assert supervisor.queue_paused() is True
    assert payload["ollama_running"] is False


def test_model_missing_state(monkeypatch):
    """Reachable server without the configured model → model_missing."""
    supervisor, client = make_supervisor(monkeypatch)
    client.reachable = True
    client.models = ["llama3.2"]

    payload = run(supervisor.refresh(allow_auto_start=False))

    assert payload["state"] == AIState.MODEL_MISSING
    assert payload["model_installed"] is False
    assert supervisor.queue_paused() is True


def test_ready_requires_smoke_test(monkeypatch):
    """READY is only reached after a successful synthetic smoke test."""
    supervisor, client = make_supervisor(monkeypatch)
    client.reachable = True
    client.models = ["qwen3:4b"]
    client.smoke_ok = False

    payload = run(supervisor.refresh(allow_auto_start=False))
    assert payload["state"] == AIState.TEMPORARILY_UNAVAILABLE
    assert supervisor.queue_paused() is True

    client.smoke_ok = True
    payload = run(supervisor.refresh(allow_auto_start=False))
    assert payload["state"] == AIState.READY
    assert supervisor.queue_paused() is False
    assert client.smoke_calls >= 1


def test_failure_classification(monkeypatch):
    """Mid-analysis failures map to the right states."""
    supervisor, client = make_supervisor(monkeypatch)

    payload = run(supervisor.on_analysis_failure(OllamaUnavailable("x")))
    assert payload["state"] == AIState.OLLAMA_NOT_RUNNING

    payload = run(supervisor.on_analysis_failure(OllamaTimeout("x")))
    assert payload["state"] == AIState.TEMPORARILY_UNAVAILABLE

    payload = run(supervisor.on_analysis_failure(OllamaModelMissing("x")))
    assert payload["state"] == AIState.MODEL_MISSING


def test_backoff_is_bounded(monkeypatch):
    """The pause schedule grows and then stays bounded."""
    supervisor, _ = make_supervisor(monkeypatch)
    seen = [supervisor.next_backoff_seconds() for _ in range(10)]
    assert seen[0] < seen[1] < seen[2]
    assert max(seen) <= 30
    assert seen[-1] == 30


def test_recovery_flow_resumes_queue(monkeypatch):
    """unavailable → recovering → ready, and the queue unpauses."""
    supervisor, client = make_supervisor(monkeypatch)
    client.reachable = False

    run(supervisor.refresh(allow_auto_start=False))
    assert supervisor.queue_paused() is True

    # Ollama comes back with the model available
    client.reachable = True
    client.models = ["qwen3:4b"]
    client.smoke_ok = True

    payload = run(supervisor.refresh(allow_auto_start=False))
    assert payload["state"] == AIState.READY
    assert supervisor.queue_paused() is False


def test_state_change_callbacks(monkeypatch):
    """Subscribers are notified once per state change."""
    supervisor, client = make_supervisor(monkeypatch)
    client.reachable = True
    client.models = ["qwen3:4b"]

    seen: list[str] = []
    supervisor.subscribe(seen.append)

    run(supervisor.refresh(allow_auto_start=False))
    assert seen == [AIState.RECOVERING, AIState.READY]

    # No change → no notification
    run(supervisor.refresh(allow_auto_start=False))
    assert seen == [AIState.RECOVERING, AIState.READY]


def test_find_ollama_executable_returns_none_when_absent(monkeypatch):
    """On a machine without Ollama the classifier reports it accurately."""
    import shutil as _shutil
    monkeypatch.setattr("backend.app.ai.supervisor.find_ollama_executable", lambda: None)
    supervisor, client = make_supervisor()
    assert supervisor.ollama_installed is False
    payload = run(supervisor.refresh(allow_auto_start=False))
    assert payload["state"] == AIState.OLLAMA_NOT_RUNNING


def test_smoke_prompt_never_contains_user_data():
    """The smoke prompt is fixed synthetic text."""
    from backend.app.ai import supervisor as sup
    assert "email" not in sup._SMOKE_PROMPT.lower()
    assert len(sup._SMOKE_PROMPT) < 100
