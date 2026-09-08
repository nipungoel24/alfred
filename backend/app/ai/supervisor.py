"""AI supervision for Alfred's local inference pipeline.

Owns the AI state machine, Ollama health polling, queue pause/backoff,
single-instance Ollama auto-start (backend-owned, never the webview),
and the synthetic smoke test that gates the READY state.

User-visible states (never Python exception names):

    initializing            startup; first health check not yet complete
    ready                   server reachable, model present, smoke passed
    ollama_not_running      server unreachable (auto-start was attempted)
    model_missing           server reachable but the configured model is absent
    temporarily_unavailable reachable but inference is failing (timeouts, bad output)
    recovering              health restored; running smoke test before READY
    error                   unexpected failure
"""

import asyncio
import logging
import os
import shutil
import subprocess
import sys
from typing import Callable

from .ollama_client import (
    OllamaClient,
    OllamaModelMissing,
    OllamaTimeout,
    OllamaUnavailable,
)

logger = logging.getLogger("alfred.ai.supervisor")

# Bounded backoff schedule (seconds) used while the queue is paused.
# Never grows beyond 30s so recovery detection stays responsive.
_BACKOFF_SCHEDULE = (5, 10, 20, 30, 30)

# Auto-start poll bound: how many seconds to wait for a freshly started
# Ollama server before giving up.
_AUTOSTART_POLL_SECONDS = 30

# The smoke test is a fixed synthetic prompt. It never contains user
# email content, and it proves the model can actually produce output.
_SMOKE_PROMPT = "Reply with exactly the word: ok"


class AIState:
    INITIALIZING = "initializing"
    READY = "ready"
    OLLAMA_NOT_RUNNING = "ollama_not_running"
    MODEL_MISSING = "model_missing"
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"
    RECOVERING = "recovering"
    ERROR = "error"


# States in which the analysis queue must not consume jobs.
_PAUSED_STATES = {
    AIState.INITIALIZING,
    AIState.OLLAMA_NOT_RUNNING,
    AIState.MODEL_MISSING,
    AIState.TEMPORARILY_UNAVAILABLE,
    AIState.RECOVERING,
    AIState.ERROR,
}


def find_ollama_executable() -> str | None:
    """Locate the Ollama executable on this machine, or None."""
    candidates: list[str] = []
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", "")
        if base:
            candidates.append(os.path.join(base, "Programs", "Ollama", "ollama.exe"))
    found = shutil.which("ollama")
    if found:
        candidates.append(found)
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    return None


class AISupervisor:
    """State machine + recovery for the local AI backend."""

    def __init__(self, client: OllamaClient, model: str):
        self.client = client
        self.model = model
        self.state: str = AIState.INITIALIZING
        self.last_error: str | None = None
        self.detail: str | None = None
        self.model_installed: bool | None = None
        self.ollama_exe: str | None = find_ollama_executable()
        self.ollama_installed: bool = self.ollama_exe is not None
        self._auto_start_attempted = False
        self._start_handle: subprocess.Popen | None = None
        self._backoff_index = 0
        self._lock = asyncio.Lock()
        self._subscribers: list[Callable[[str], None]] = []

    # ── State plumbing ──

    def subscribe(self, callback: Callable[[str], None]):
        """Register a synchronous callback invoked on state changes."""
        self._subscribers.append(callback)

    async def _set_state(self, state: str, error: str | None = None,
                         detail: str | None = None):
        changed = self.state != state
        self.state = state
        self.last_error = error
        self.detail = detail
        if changed:
            for callback in self._subscribers:
                try:
                    callback(state)
                except Exception:
                    pass

    def queue_paused(self) -> bool:
        """True when inference consumption must pause."""
        return self.state in _PAUSED_STATES

    def payload(self) -> dict:
        """Observer-facing status payload (never secrets)."""
        return {
            "state": self.state,
            "model": self.model,
            "model_installed": self.model_installed,
            "ollama_installed": self.ollama_installed,
            "ollama_running": self.state not in (
                AIState.INITIALIZING, AIState.OLLAMA_NOT_RUNNING,
            ),
            "last_error": self.last_error,
            "detail": self.detail,
        }

    # ── Health / classification ──

    async def _tags(self) -> tuple[bool, list[str]]:
        """(reachable, model names) from Ollama's /api/tags."""
        try:
            r = await self.client.health()
            models = [str(m.get("name", "")) for m in r.get("models", [])]
            return True, models
        except Exception:
            return False, []

    async def refresh(self, allow_auto_start: bool = True) -> dict:
        """Run a full health check and update the state machine.

        Transitions to READY only after a successful synthetic smoke
        test, so "ready" means inference actually works.
        """
        async with self._lock:
            reachable, models = await self._tags()

            if not reachable:
                if not self._auto_start_attempted and allow_auto_start:
                    await self._try_auto_start()
                    reachable, models = await self._tags()
                if not reachable:
                    self.model_installed = None
                    await self._set_state(
                        AIState.OLLAMA_NOT_RUNNING,
                        error="Ollama server is not running",
                        detail=(
                            "Ollama is installed but not running; Alfred will "
                            "retry automatically."
                            if self.ollama_installed
                            else "Ollama does not appear to be installed."
                        ),
                    )
                    return self.payload()

            self.model_installed = self.model in models
            if not self.model_installed:
                await self._set_state(
                    AIState.MODEL_MISSING,
                    error=f'Model "{self.model}" is not installed',
                    detail=f'Pull the model with: ollama pull {self.model}',
                )
                return self.payload()

            if self.state != AIState.READY:
                await self._set_state(AIState.RECOVERING)

            if await self._smoke_test():
                self._backoff_index = 0
                await self._set_state(AIState.READY)
            else:
                await self._set_state(
                    AIState.TEMPORARILY_UNAVAILABLE,
                    error="Local AI smoke test failed",
                    detail="Alfred will keep retrying in the background.",
                )
            return self.payload()

    # ── Auto-start (backend-owned, single instance, bounded) ──

    async def _try_auto_start(self):
        """Start the Ollama server once if installed and not running.

        Uses a detached, window-less process owned by this backend.
        Never starts a second instance when one is already responding.
        Never downloads models.
        """
        self._auto_start_attempted = True
        exe = find_ollama_executable()
        if not exe:
            return
        logger.info("ollama_auto_start_attempt exe=%s", exe)
        try:
            if sys.platform == "win32":
                flags = (
                    subprocess.CREATE_NEW_PROCESS_GROUP
                    | subprocess.DETACHED_PROCESS
                    | subprocess.CREATE_NO_WINDOW
                )
                self._start_handle = subprocess.Popen(
                    [exe, "serve"],
                    creationflags=flags,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                )
            else:
                self._start_handle = subprocess.Popen(
                    [exe, "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                    close_fds=True,
                )
        except Exception as exc:
            logger.warning("ollama_auto_start_failed: %s", exc)
            return
        for _ in range(_AUTOSTART_POLL_SECONDS):
            reachable, _ = await self._tags()
            if reachable:
                logger.info("ollama_auto_start_success")
                return
            await asyncio.sleep(1.0)
        logger.warning("ollama_auto_start_timeout_after=%ss", _AUTOSTART_POLL_SECONDS)

    # ── Smoke test ──

    async def _smoke_test(self) -> bool:
        """Synthetic inference using a fixed prompt — never user email."""
        try:
            text, _ = await self.client.generate(
                self.model, _SMOKE_PROMPT, temperature=0.0
            )
            return bool(text.strip())
        except Exception as exc:
            logger.warning("ai_smoke_test_failed: %s", type(exc).__name__)
            return False

    # ── Failure classification + queue pause ──

    async def on_analysis_failure(self, exc: Exception) -> dict:
        """Classify a mid-analysis failure and update state."""
        async with self._lock:
            if isinstance(exc, OllamaUnavailable):
                await self._set_state(
                    AIState.OLLAMA_NOT_RUNNING,
                    error="Ollama server is not reachable",
                )
            elif isinstance(exc, OllamaTimeout):
                await self._set_state(
                    AIState.TEMPORARILY_UNAVAILABLE,
                    error="Local AI timed out",
                )
            elif isinstance(exc, OllamaModelMissing):
                self.model_installed = False
                await self._set_state(
                    AIState.MODEL_MISSING,
                    error=f'Model "{self.model}" is not installed',
                )
            return self.payload()

    def next_backoff_seconds(self) -> int:
        """Next pause duration from the bounded backoff schedule."""
        delay = _BACKOFF_SCHEDULE[
            min(self._backoff_index, len(_BACKOFF_SCHEDULE) - 1)
        ]
        self._backoff_index = min(
            self._backoff_index + 1, len(_BACKOFF_SCHEDULE) - 1
        )
        return delay

    def reset_backoff(self):
        self._backoff_index = 0

    async def wait_and_recheck(self) -> dict:
        """Sleep the bounded backoff, then refresh health.

        Used by the analysis worker while the queue is paused so queued
        work is retained and automatically resumed when AI recovers.
        """
        await asyncio.sleep(self.next_backoff_seconds())
        return await self.refresh()
