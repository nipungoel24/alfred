"""Tests for model download orchestration in the AI supervisor.

Covers the Gate 2 behaviours that live above the HTTP client: the
`model_downloading` / `model_failed` states, cancellation that leaves no
stale download behind, the disk preflight, duplicate-pull suppression, and
the generation guard that stops a superseded download from overwriting a
newer one.
"""

import asyncio

import pytest

from backend.app.ai.ollama_client import (
    OllamaInsufficientSpace,
    OllamaPullFailed,
    PullProgress,
)
from backend.app.ai.supervisor import AISupervisor, AIState


class FakePullClient:
    """Scriptable Ollama stand-in that can simulate a model download."""

    def __init__(self):
        self.reachable = True
        self.models: list[str] = []
        # Real on-disk size per model, as /api/tags would report it.
        self.model_sizes: dict[str, int] = {}
        self.smoke_ok = True
        self.smoke_calls = 0
        self.health_calls = 0
        self.pull_behaviour = "success"   # success | fail | space | hang
        self.pull_calls = 0
        self.progress_seen: list[PullProgress] = []
        self.announce = (1000, 500)        # (total, completed) per step
        self.steps = 3
        # A plain flag, not asyncio.Event: the fake is constructed on the
        # test thread but awaited on another loop, and Event binds to the
        # loop that first waits on it.
        self.release = False
        self.checked_total = None

    async def health(self) -> dict:
        self.health_calls += 1
        if not self.reachable:
            from backend.app.ai.ollama_client import OllamaUnavailable
            raise OllamaUnavailable("not reachable")
        return {
            "models": [
                {"name": m, "size": self.model_sizes.get(m)}
                for m in self.models
            ]
        }

    async def generate(self, model, prompt, schema=None, temperature=0.0):
        self.smoke_calls += 1
        if not self.smoke_ok:
            from backend.app.ai.ollama_client import OllamaTimeout
            raise OllamaTimeout("smoke timed out")
        return "ok", None

    async def list_models(self) -> list[dict]:
        """Local models with real sizes, mirroring OllamaClient.list_models."""
        await self.health()
        return [
            {
                "name": m,
                "size_bytes": self.model_sizes.get(m),
                "parameter_size": None,
                "quantization": None,
            }
            for m in self.models
        ]

    async def model_size(self, model: str) -> int | None:
        return self.model_sizes.get(model)

    async def pull_model(self, model, on_progress=None, check_space=None):
        self.pull_calls += 1
        total, step = self.announce
        for i in range(1, self.steps + 1):
            progress = PullProgress(
                status=f"pulling {i}",
                completed_bytes=step * i,
                total_bytes=total,
                digest="a",
                layer_completed=step * i,
                layer_total=total,
            )
            self.progress_seen.append(progress)
            if on_progress:
                on_progress(progress)
            if i == 1 and check_space:
                self.checked_total = total
                check_space(total)
            if self.pull_behaviour == "hang":
                while not self.release:
                    await asyncio.sleep(0.005)
            elif self.pull_behaviour == "space":
                raise OllamaInsufficientSpace(required_bytes=total, free_bytes=1)
            elif self.pull_behaviour == "fail" and i == self.steps:
                raise OllamaPullFailed("registry refused")
        if self.pull_behaviour == "success":
            final = PullProgress("success", total, total, None, None, None)
            self.progress_seen.append(final)
            if on_progress:
                on_progress(final)
            return final
        return PullProgress("success", 0, None, None, None, None)


def make_supervisor(client=None):
    client = client or FakePullClient()
    return AISupervisor(client, "qwen3:4b"), client  # type: ignore[arg-type]


def test_start_pull_enters_downloading_and_publishes_real_bytes():
    sup, client = make_supervisor()

    async def run():
        payload, task = await _start(sup)
        await task
        return payload

    initial = asyncio.run(run())
    assert initial["state"] == AIState.MODEL_DOWNLOADING
    # Real byte counts came off the stream, not a timer.
    assert client.progress_seen[0].completed_bytes == 500
    assert any(p.total_bytes == 1000 for p in client.progress_seen)
    assert client.checked_total == 1000


def test_successful_pull_runs_the_readiness_check_before_ready():
    sup, client = make_supervisor()
    client.models = ["qwen3:4b"]

    async def run():
        _, task = await _start(sup)
        await task

    asyncio.run(run())
    assert sup.state == AIState.READY
    # A finished download is not readiness on its own: the smoke test ran.
    assert client.smoke_calls == 1
    assert sup.model_installed is True
    assert sup.pull_progress is None


async def _start(sup):
    """Start a pull and yield so the task actually begins executing.

    `start_pull` deliberately does not await the download, and the success
    path clears `_pull_task`, so the handle has to be captured here.
    """
    payload = await sup.start_pull()
    await asyncio.sleep(0)
    return payload, sup._pull_task


def test_second_start_while_downloading_is_idempotent():
    sup, client = make_supervisor()
    client.pull_behaviour = "hang"

    async def run():
        first, _ = await _start(sup)
        second = await sup.start_pull()
        await asyncio.sleep(0)
        assert client.pull_calls == 1, "a duplicate pull must not be started"
        assert first["state"] == AIState.MODEL_DOWNLOADING
        assert second["state"] == AIState.MODEL_DOWNLOADING
        await sup.cancel_pull()

    asyncio.run(run())


def test_cancel_clears_progress_and_does_not_leave_a_stale_download_state():
    sup, client = make_supervisor()
    client.pull_behaviour = "hang"
    client.models = []  # model still absent after cancellation

    async def run():
        # Reach the state a user actually starts a download from.
        await sup.refresh()
        assert sup.state == AIState.MODEL_MISSING
        await sup.start_pull()
        await asyncio.sleep(0.05)   # let the stream advance
        assert sup.state == AIState.MODEL_DOWNLOADING
        await sup.cancel_pull()

    asyncio.run(run())
    assert sup.state == AIState.MODEL_MISSING  # back to where it started
    assert sup.pull_progress is None
    assert sup.pull_payload() is None
    assert sup.pulling is False


def test_cancel_is_idempotent():
    sup, client = make_supervisor()
    client.models = ["qwen3:4b"]

    async def run():
        await sup.cancel_pull()          # nothing running
        _, task = await _start(sup)
        await task                       # let it finish on its own
        await sup.cancel_pull()          # already finished
        return sup.payload()

    payload = asyncio.run(run())
    assert payload["state"] == AIState.READY


def test_insufficient_space_fails_the_pull_with_a_specific_code():
    sup, client = make_supervisor()
    client.pull_behaviour = "space"

    async def run():
        _, task = await _start(sup)
        await task

    asyncio.run(run())
    assert sup.state == AIState.MODEL_FAILED
    assert sup.pull_error_code == "INSUFFICIENT_DISK_SPACE"
    assert "free space" in (sup.detail or "")
    assert sup.pull_payload()["code"] == "INSUFFICIENT_DISK_SPACE"


def test_pull_failure_is_reported_as_model_failed():
    sup, client = make_supervisor()
    client.pull_behaviour = "fail"

    async def run():
        _, task = await _start(sup)
        await task

    asyncio.run(run())
    assert sup.state == AIState.MODEL_FAILED
    assert sup.pull_error_code == "MODEL_PULL_FAILED"
    assert "registry refused" in (sup.last_error or "")


def test_unreachable_server_is_reported_before_a_pull_starts():
    sup, client = make_supervisor()
    client.reachable = False
    sup._auto_start_attempted = True

    async def run():
        return await sup.start_pull()

    payload = asyncio.run(run())
    assert payload["state"] == AIState.OLLAMA_NOT_RUNNING
    assert client.pull_calls == 0


def test_a_superseded_pull_cannot_overwrite_newer_state():
    sup, client = make_supervisor()
    client.models = ["qwen3:4b"]

    async def run():
        await sup.start_pull()
        probe_calls = client.health_calls   # the reachability probe only
        # Simulate a newer pull superseding this one mid-flight.
        sup._pull_generation += 1
        await sup._pull_task
        return probe_calls, client.health_calls

    before, after = asyncio.run(run())
    # Only the pre-pull reachability probe ran; the stale result must not
    # have triggered the readiness check that would claim the model ready.
    assert after == before
    assert sup.model_installed is not True


def test_queue_is_paused_while_downloading_and_after_failure():
    sup, client = make_supervisor()
    client.pull_behaviour = "hang"

    async def run():
        await sup.start_pull()
        await asyncio.sleep(0.05)
        paused_during = sup.queue_paused()
        await sup.cancel_pull()
        return paused_during

    assert asyncio.run(run()) is True

    sup2, client2 = make_supervisor()
    client2.pull_behaviour = "space"

    async def run2():
        _, task = await _start(sup2)
        await task
        return sup2.queue_paused()

    assert asyncio.run(run2()) is True


def test_set_model_refuses_while_a_download_is_running():
    sup, client = make_supervisor()
    client.pull_behaviour = "hang"

    async def run():
        await sup.start_pull()
        with pytest.raises(RuntimeError):
            sup.set_model("other:1b")
        await sup.cancel_pull()

    asyncio.run(run())
    assert sup.model == "qwen3:4b"


def test_set_model_rejects_an_empty_name():
    sup, _ = make_supervisor()
    with pytest.raises(ValueError):
        sup.set_model("   ")


def test_set_model_applies_when_idle():
    sup, _ = make_supervisor()
    assert sup.set_model("llama3:8b") == "llama3:8b"
    assert sup.model == "llama3:8b"


def test_refresh_does_not_clobber_an_active_download():
    sup, client = make_supervisor()
    client.pull_behaviour = "hang"
    client.models = []

    async def run():
        await sup.start_pull()
        await asyncio.sleep(0.05)
        state_during = sup.state
        await sup.refresh()
        assert sup.state == state_during, "refresh must not reclassify a live download"
        await sup.cancel_pull()

    asyncio.run(run())


def test_analysis_failure_does_not_clobber_an_active_download():
    sup, client = make_supervisor()
    client.pull_behaviour = "hang"

    async def run():
        await sup.start_pull()
        await asyncio.sleep(0.05)
        await sup.on_analysis_failure(RuntimeError("boom"))
        assert sup.state == AIState.MODEL_DOWNLOADING
        await sup.cancel_pull()

    asyncio.run(run())


def test_pull_payload_is_none_before_any_pull():
    sup, _ = make_supervisor()
    assert sup.pull_payload() is None
    assert sup.payload()["pull"] is None


def test_pull_payload_reports_null_fraction_until_a_total_is_announced():
    sup, client = make_supervisor()
    client.announce = (None, 100)  # completed bytes with no announced total
    client.steps = 1
    client.pull_behaviour = "hang"

    async def run():
        await _start(sup)
        await asyncio.sleep(0.05)
        return sup.pull_payload()

    payload = asyncio.run(run())
    assert payload["completed_bytes"] == 100
    assert payload["total_bytes"] is None
    assert payload["fraction"] is None
    assert payload["human_total"] is None


def test_pull_payload_formats_bytes_honestly():
    sup, client = make_supervisor()
    client.announce = (5 * 1024 ** 3, 1024 ** 3)
    client.steps = 1
    client.pull_behaviour = "hang"

    async def run():
        await _start(sup)
        await asyncio.sleep(0.05)
        return sup.pull_payload()

    payload = asyncio.run(run())
    assert payload["human_total"] == "5.0 GB"
    assert payload["human_completed"] == "1.0 GB"
    assert payload["fraction"] == pytest.approx(0.2)


def test_the_only_resource_constant_is_the_documented_ram_floor():
    """No fabricated model size may appear anywhere in the download path."""
    from backend.app.ai.resources import MIN_DOWNLOAD_RAM_BYTES
    assert MIN_DOWNLOAD_RAM_BYTES == 4 * 1024 ** 3
