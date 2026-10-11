"""AI supervision for Alfred's local inference pipeline.

Owns the AI state machine, Ollama health polling, queue pause/backoff,
single-instance Ollama auto-start (backend-owned, never the webview),
model download with real progress, and the synthetic smoke test that
gates the READY state.

User-visible states (never Python exception names):

    initializing            startup; first health check not yet complete
    ready                   server reachable, model present, smoke passed
    ollama_not_running      server unreachable (auto-start was attempted)
    model_missing           server reachable but the configured model is absent
    model_downloading       a model pull is in flight; progress is real bytes
    model_failed            the last pull failed; retry is offered
    temporarily_unavailable reachable but inference is failing (timeouts, bad output)
    recovering              health restored; running smoke test before READY
    error                   unexpected failure

The `docs/Phases.md` Gate 2 scope lists this machine's required model states
as MODEL_RUNTIME_MISSING / MODEL_RUNTIME_STARTING / MODEL_DOWNLOAD_REQUIRED /
MODEL_DOWNLOADING / MODEL_READY / MODEL_FAILED. The first four map onto
`ollama_not_running`, `initializing`, `model_missing` and `ready` as already
shipped and already consumed by the frontend; `model_downloading` and
`model_failed` are the two that did not exist and are added here. Renaming
the shipped vocabulary would break the frontend contract and its tests for
no behavioural gain, so it is deliberately preserved.
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
    OllamaInsufficientSpace,
    OllamaModelMissing,
    OllamaPullFailed,
    OllamaTimeout,
    OllamaUnavailable,
    PullProgress,
)
from .resources import check_for_model_download, human_bytes

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
    MODEL_DOWNLOADING = "model_downloading"
    MODEL_FAILED = "model_failed"
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"
    RECOVERING = "recovering"
    ERROR = "error"


# States in which the analysis queue must not consume jobs.
_PAUSED_STATES = {
    AIState.INITIALIZING,
    AIState.OLLAMA_NOT_RUNNING,
    AIState.MODEL_MISSING,
    AIState.MODEL_DOWNLOADING,
    AIState.MODEL_FAILED,
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
        # Model download. `_pull_generation` invalidates any in-flight
        # result once a newer pull supersedes it, so a slow old download
        # can never overwrite the state of a newer one.
        self._pull_task: asyncio.Task | None = None
        self._pull_generation = 0
        self.pull_progress: dict | None = None
        self.pull_error_code: str | None = None
        self.pull_error_detail: str | None = None

    # â”€â”€ State plumbing â”€â”€

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
                    # A subscriber must not be able to break the state
                    # machine, but a silent drop would hide a real fault
                    # (Rules Â§1.15), so it is logged with context.
                    logger.exception("ai_state_subscriber_failed state=%s", state)

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
            "pull": self.pull_payload(),
        }

    def pull_payload(self) -> dict | None:
        """Current download progress, or None when no pull has been started.

        Every byte figure here is read from Ollama's own stream; nothing is
        interpolated, estimated, or animated.
        """
        if self.pull_progress is None and self.pull_error_code is None:
            return None
        progress = self.pull_progress or {}
        completed = progress.get("completed_bytes")
        total = progress.get("total_bytes")
        return {
            "model": progress.get("model", self.model),
            "status": progress.get("status"),
            "completed_bytes": completed,
            "total_bytes": total,
            # Null â€” never a guess â€” when Ollama has not announced a total.
            "fraction": (
                min(1.0, completed / total) if total else None
            ) if isinstance(completed, int) and isinstance(total, int) else None,
            "human_completed": human_bytes(completed) if isinstance(completed, int) else None,
            "human_total": human_bytes(total) if isinstance(total, int) else None,
            "running": self._pull_task is not None and not self._pull_task.done(),
            "code": self.pull_error_code,
            "error": self.pull_error_detail,
        }


    # â”€â”€ Health / classification â”€â”€

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
        if self._pull_owns_state():
            # A download owns the state machine. Re-running health now
            # would report the model missing while it is half-installed.
            return self.payload()
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

    # â”€â”€ Model download â”€â”€

    @property
    def pulling(self) -> bool:
        """True while a download task is actually in flight."""
        return self._pull_task is not None and not self._pull_task.done()

    def _pull_owns_state(self) -> bool:
        """True when a download task is running and is not the caller.

        `refresh()` is re-entered by the pull itself once the model is on
        disk; that call must proceed, while a refresh arriving from the
        analysis worker must not clobber a live download.
        """
        task = self._pull_task
        return task is not None and not task.done() and task is not asyncio.current_task()

    def set_model(self, model: str) -> str:
        """Select the model to use. Refuses while a pull is in flight.

        Changing the target underneath a running download would make the
        announced progress refer to a model that is no longer wanted.
        """
        model = (model or "").strip()
        if not model:
            raise ValueError("model must not be empty")
        if self.pulling:
            raise RuntimeError("cannot change the model while a download is running")
        self.model = model
        return self.model

    async def start_pull(self, model: str | None = None) -> dict:
        """Begin downloading the configured model. Idempotent.

        A second call while a download runs returns the live progress
        instead of starting a duplicate pull: Ollama cannot usefully pull
        the same model twice, and two tasks would fight over the state
        machine.
        """
        if model:
            self.set_model(model)

        if self.pulling:
            return self.payload()

        reachable, _ = await self._tags()
        if not reachable:
            # Auto-start once so "start the download" also gets the
            # server up, which is what the first-run screen promises.
            if not self._auto_start_attempted:
                await self._try_auto_start()
                reachable, _ = await self._tags()
            if not reachable:
                await self._set_state(
                    AIState.OLLAMA_NOT_RUNNING,
                    error="Ollama server is not running",
                    detail="Start Ollama, then try the download again.",
                )
                return self.payload()

        self._pull_generation += 1
        generation = self._pull_generation
        previous_state = self.state
        self.pull_progress = {
            "model": self.model, "status": "starting",
            "completed_bytes": 0, "total_bytes": None,
        }
        self.pull_error_code = None
        self.pull_error_detail = None
        await self._set_state(AIState.MODEL_DOWNLOADING)
        self._pull_task = asyncio.create_task(
            self._run_pull(self.model, generation, previous_state)
        )
        return self.payload()

    async def cancel_pull(self) -> dict:
        """Cancel the in-flight download. Idempotent and safe.

        Cancelling closes the HTTP stream to Ollama, which is what makes
        Ollama abandon the pull. Completed layers stay on disk, so the
        next pull resumes at layer granularity rather than restarting.
        """
        task = self._pull_task
        if task is None or task.done():
            return self.payload()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        except Exception:  # noqa: BLE001 - the task records its own failure
            logger.exception("ai_pull_cancel_await_failed")
        return self.payload()

    async def _run_pull(self, model: str, generation: int, previous_state: str):
        """Download `model`, publishing real progress as it arrives."""

        def on_progress(progress: PullProgress):
            self.pull_progress = {
                "model": model,
                "status": progress.status,
                "completed_bytes": progress.completed_bytes,
                "total_bytes": progress.total_bytes,
            }

        def check_space(total: int | None):
            # Raised inside the stream so the download stops before more
            # layer bytes move, not after the disk is already full.
            check = check_for_model_download(total)
            if check.blocking:
                raise OllamaInsufficientSpace(
                    required_bytes=total or 0,
                    free_bytes=check.disk.free_bytes,
                )

        try:
            await self.client.pull_model(
                model, on_progress=on_progress, check_space=check_space
            )
        except asyncio.CancelledError:
            # Deliberate cancellation is not a failure: clear the progress
            # and fall back so the UI can never be left showing a stale
            # download that is no longer running.
            if generation == self._pull_generation:
                self.pull_progress = None
                self.pull_error_code = None
                self.pull_error_detail = None
                await self._set_state(previous_state)
                logger.info("model_pull_cancelled model=%s", model)
            raise
        except OllamaInsufficientSpace as exc:
            if generation == self._pull_generation:
                self.pull_progress = None
                self.pull_error_code = "INSUFFICIENT_DISK_SPACE"
                self.pull_error_detail = (
                    f"Not enough free space to download {model}. "
                    f"About {human_bytes(max(0, exc.required_bytes - exc.free_bytes))} "
                    f"more is needed."
                )
                await self._set_state(
                    AIState.MODEL_FAILED,
                    error=self.pull_error_detail,
                    detail=self.pull_error_detail,
                )
                logger.warning("model_pull_insufficient_space model=%s required=%s free=%s",
                               model, exc.required_bytes, exc.free_bytes)
            return
        except (OllamaPullFailed, OllamaUnavailable, OllamaTimeout) as exc:
            if generation == self._pull_generation:
                self.pull_progress = None
                self.pull_error_code = "MODEL_PULL_FAILED"
                self.pull_error_detail = str(exc) or type(exc).__name__
                await self._set_state(
                    AIState.MODEL_FAILED,
                    error=self.pull_error_detail,
                    detail="The download did not finish. You can try again.",
                )
                logger.warning("model_pull_failed model=%s error=%s",
                               model, type(exc).__name__)
            return
        except Exception as exc:  # noqa: BLE001 - converted to a typed state
            if generation == self._pull_generation:
                self.pull_progress = None
                self.pull_error_code = "MODEL_PULL_FAILED"
                self.pull_error_detail = type(exc).__name__
                await self._set_state(
                    AIState.MODEL_FAILED,
                    error=f"Model download failed: {type(exc).__name__}",
                )
                logger.exception("model_pull_unexpected_failure model=%s", model)
            return

        if generation != self._pull_generation:
            # A newer pull superseded this one; its result must not land.
            logger.info("model_pull_superseded model=%s generation=%s",
                        model, generation)
            return

        self.model_installed = True
        self.pull_progress = None
        self.pull_error_code = None
        self.pull_error_detail = None
        logger.info("model_pull_complete model=%s", model)
        # A finished download is not readiness. Run the real health check
        # and smoke test so READY still means inference actually works.
        await self.refresh()

    # â”€â”€ Auto-start (backend-owned, single instance, bounded) â”€â”€

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

    # â”€â”€ Smoke test â”€â”€

    async def _smoke_test(self) -> bool:
        """Synthetic inference using a fixed prompt â€” never user email."""
        try:
            text, _ = await self.client.generate(
                self.model, _SMOKE_PROMPT, temperature=0.0
            )
            return bool(text.strip())
        except Exception as exc:
            logger.warning("ai_smoke_test_failed: %s", type(exc).__name__)
            return False

    # â”€â”€ Failure classification + queue pause â”€â”€

    async def on_analysis_failure(self, exc: Exception) -> dict:
        """Classify a mid-analysis failure and update state."""
        if self._pull_owns_state():
            # A download in flight is not an analysis failure, and
            # reclassifying the state would strand it as an error.
            return self.payload()
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
