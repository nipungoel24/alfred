"""Regression tests for the model-download path: real streaming progress,
incremental NDJSON decoding, cancellation, and the resource preflight."""

import asyncio

import httpx
import pytest

from backend.app.ai.ollama_client import (
    LayerProgressAggregator,
    NdjsonStreamDecoder,
    OllamaClient,
    OllamaInsufficientSpace,
    OllamaPullFailed,
    PullProgress,
    iter_ndjson_records,
)
from backend.app.ai.resources import (
    MIN_DOWNLOAD_RAM_BYTES,
    DiskStatus,
    check_for_model_download,
    disk_status,
    human_bytes,
    installed_ram_bytes,
    ollama_models_dir,
)


# ── NDJSON decoding ──────────────────────────────────────────────────


def test_records_split_across_network_chunks_are_reassembled():
    payload = b'{"status":"pulling manifest"}\n{"digest":"a","total":100,"completed":0}\n'
    # Split mid-object and mid-line on purpose.
    chunks = [payload[:20], payload[20:33], payload[33:60], payload[60:]]
    records = list(iter_ndjson_records(chunks))
    assert records == [
        {"status": "pulling manifest"},
        {"digest": "a", "total": 100, "completed": 0},
    ]


def test_incomplete_final_record_without_newline_is_emitted_by_flush():
    decoder = NdjsonStreamDecoder()
    assert decoder.feed(b'{"status":"succ') == []
    assert decoder.feed(b'ess"}') == []   # still no newline: not yet
    assert decoder.flush() == [{"status": "success"}]


def test_incomplete_final_record_is_not_emitted_until_flush():
    decoder = NdjsonStreamDecoder()
    # A terminated record is emitted immediately...
    assert decoder.feed(b'{"status":"success"}\n') == [{"status": "success"}]
    # ...but a complete record whose final newline never arrived (the
    # server closed the stream) is held back until flush.
    assert decoder.feed(b'{"status":"trailing"}') == []
    assert decoder.flush() == [{"status": "trailing"}]


def test_unparseable_incomplete_tail_is_dropped_not_invented():
    # A half-written object is not a record; inventing one would be worse
    # than dropping it, because a caller would act on a fabricated status.
    decoder = NdjsonStreamDecoder()
    assert decoder.feed(b'{"status":"trail') == []
    assert decoder.flush() == []
    assert decoder.malformed_count == 1


def test_malformed_record_is_dropped_without_losing_neighbours():
    records = list(iter_ndjson_records([
        b'{"status":"a"}\nnot json at all\n{"status":"b"}\n',
    ]))
    assert records == [{"status": "a"}, {"status": "b"}]
    decoder = NdjsonStreamDecoder()
    decoder.feed(b"broken\n")
    assert decoder.malformed_count == 1


def test_non_object_record_is_dropped():
    records = list(iter_ndjson_records([b'["array"]\n"string"\n{"ok":1}\n']))
    assert records == [{"ok": 1}]


def test_blank_lines_are_ignored():
    assert list(iter_ndjson_records([b'\n\n  \n{"a":1}\n\n'])) == [{"a": 1}]


def test_multi_byte_utf8_split_across_chunks():
    payload = '{"status":"\u00e9t\u00e9"}\n'.encode("utf-8")
    records = list(iter_ndjson_records([payload[:8], payload[8:]]))
    assert records == [{"status": "\u00e9t\u00e9"}]


# ── Layer aggregation ────────────────────────────────────────────────


def test_repeated_updates_for_one_digest_do_not_double_count():
    agg = LayerProgressAggregator()
    agg.observe({"digest": "a", "total": 1000, "completed": 0})
    progress = agg.observe({"digest": "a", "total": 1000, "completed": 250})
    assert progress.completed_bytes == 250
    assert progress.total_bytes == 1000
    assert agg.announced_total == 1000


def test_multiple_layers_are_summed_once_each():
    agg = LayerProgressAggregator()
    agg.observe({"digest": "a", "total": 1000, "completed": 100})
    agg.observe({"digest": "b", "total": 2000, "completed": 500})
    progress = agg.observe({"digest": "a", "total": 1000, "completed": 900})
    assert progress.total_bytes == 3000
    assert progress.completed_bytes == 1400  # 900 (a, latest) + 500 (b)


def test_status_records_without_bytes_do_not_invent_a_total():
    agg = LayerProgressAggregator()
    progress = agg.observe({"status": "pulling manifest"})
    assert progress.total_bytes is None
    assert progress.completed_bytes == 0
    assert progress.fraction is None
    assert progress.status == "pulling manifest"


def test_status_is_retained_across_layer_records():
    agg = LayerProgressAggregator()
    agg.observe({"status": "pulling sha256:abc"})
    progress = agg.observe({"digest": "sha256:abc", "total": 10, "completed": 1})
    assert progress.status == "pulling sha256:abc"


def test_fraction_is_none_until_a_total_is_announced():
    assert PullProgress("x", 50, None, None, None, None).fraction is None


def test_fraction_is_capped_at_one():
    assert PullProgress("x", 150, 100, None, None, None).fraction == 1.0


def test_fraction_reflects_real_bytes():
    assert PullProgress("x", 250, 1000, None, None, None).fraction == 0.25


# ── Streaming pull through a real transport ──────────────────────────


class _ChunkStream(httpx.AsyncByteStream):
    """Yields each chunk on its own read, like a real socket.

    `gate` blocks every chunk once `block_after` chunks have been yielded,
    which is how a mid-download stall is reproduced deterministically.
    """

    def __init__(self, chunks, gate=None, block_after=None):
        self._chunks = chunks
        self._gate = gate
        self._block_after = block_after
        self._yielded = 0

    async def __aiter__(self):
        for chunk in self._chunks:
            if self._gate is not None and self._block_after is not None:
                if self._yielded >= self._block_after:
                    await self._gate.wait()
            yield chunk
            self._yielded += 1

    async def aclose(self):
        return None


class _StreamTransport(httpx.AsyncBaseTransport):
    def __init__(self, status_code, chunks, gate=None, block_after=None):
        self.status_code = status_code
        self._chunks = chunks
        self._gate = gate
        self._block_after = block_after

    async def handle_async_request(self, request):
        return httpx.Response(
            self.status_code,
            stream=_ChunkStream(self._chunks, self._gate, self._block_after),
            request=request,
        )


def _lines(records):
    return (f"{r}\n".encode("utf-8") for r in records)


def _client_for(status, records, gate=None):
    import json as _json
    chunks = [b"".join(_lines([_json.dumps(r) for r in records]))]
    transport = _StreamTransport(status, chunks, gate)
    http = httpx.AsyncClient(transport=transport, base_url="http://ollama.test")
    return OllamaClient("http://ollama.test", client=http), http


def test_pull_reports_real_progress_and_completes():
    records = [
        {"status": "pulling manifest"},
        {"digest": "a", "total": 1000, "completed": 0},
        {"digest": "a", "total": 1000, "completed": 400},
        {"digest": "b", "total": 500, "completed": 0},
        {"digest": "a", "total": 1000, "completed": 1000},
        {"digest": "b", "total": 500, "completed": 500},
        {"status": "success"},
    ]
    client, http = _client_for(200, records)
    seen: list[PullProgress] = []

    async def run():
        async with http:
            return await client.pull_model("m", on_progress=seen.append)

    final = asyncio.run(run())
    assert final.status == "success"
    assert final.completed_bytes == 1500
    assert final.total_bytes == 1500
    # Progress only ever moved forward — no timer, no synthetic ramp.
    totals = [p.completed_bytes for p in seen]
    assert totals == sorted(totals)
    assert seen[0].total_bytes is None  # before the manifest was announced
    assert any(p.total_bytes == 1500 for p in seen)


def test_pull_splits_records_across_chunks_while_streaming():
    body = (
        b'{"status":"pulling manifest"}\n{"digest":"a","total":10,'
        b'"completed":5}\n{"status":"success"}\n'
    )
    # Cut so the digest record itself is split across two reads.
    cut = body.index(b'"digest"') + 3
    transport = _StreamTransport(200, [body[:cut], body[cut:cut + 20], body[cut + 20:]])
    http = httpx.AsyncClient(transport=transport, base_url="http://o.test")
    client = OllamaClient("http://o.test", client=http)

    async def run():
        async with http:
            return await client.pull_model("m")

    final = asyncio.run(run())
    assert final.status == "success"
    assert final.total_bytes == 10
    assert final.completed_bytes == 5


def test_pull_error_record_raises_and_is_not_reported_as_success():
    client, http = _client_for(200, [{"status": "pulling manifest"},
                                     {"error": "model not found"}])

    async def run():
        async with http:
            return await client.pull_model("m")

    with pytest.raises(OllamaPullFailed, match="model not found"):
        asyncio.run(run())


def test_pull_non_success_terminal_status_raises():
    client, http = _client_for(200, [{"status": "pulling manifest"}])

    async def run():
        async with http:
            return await client.pull_model("m")

    with pytest.raises(OllamaPullFailed, match="without reporting success"):
        asyncio.run(run())


def test_pull_http_error_status_raises():
    client, http = _client_for(404, [{"error": "no such model"}])

    async def run():
        async with http:
            return await client.pull_model("m")

    with pytest.raises(OllamaPullFailed, match="HTTP 404"):
        asyncio.run(run())


def test_space_check_runs_once_with_the_announced_total_before_progress():
    records = [
        {"status": "pulling manifest"},
        {"digest": "a", "total": 1000, "completed": 0},
        {"digest": "a", "total": 1000, "completed": 600},
        {"digest": "b", "total": 2000, "completed": 0},
        {"status": "success"},
    ]
    client, http = _client_for(200, records)
    checked: list[int | None] = []

    def check(total):
        checked.append(total)

    async def run():
        async with http:
            return await client.pull_model("m", check_space=check)

    asyncio.run(run())
    # Once only, and with the first announced total — not the final one,
    # so the decision is taken before the bodies move.
    assert checked == [1000]


def test_space_check_aborts_the_download_before_it_fills_the_disk():
    records = [
        {"digest": "a", "total": 5_000_000_000, "completed": 0},
        {"digest": "a", "total": 5_000_000_000, "completed": 4_000_000_000},
        {"status": "success"},
    ]
    client, http = _client_for(200, records)

    def check(total):
        raise OllamaInsufficientSpace(required_bytes=total, free_bytes=10)

    async def run():
        async with http:
            return await client.pull_model("m", check_space=check)

    with pytest.raises(OllamaInsufficientSpace):
        asyncio.run(run())


def test_cancelling_the_pull_task_closes_the_stream():
    import asyncio as _asyncio

    gate = _asyncio.Event()
    # Each record is one chunk. The stream yields the first two, then
    # stalls forever — exactly the shape of a download interrupted
    # mid-transfer.
    chunks = [
        b'{"status":"pulling manifest"}\n',
        b'{"digest":"a","total":1000,"completed":0}\n',
        b'{"digest":"a","total":1000,"completed":900}\n',
        b'{"status":"success"}\n',
    ]
    transport = _StreamTransport(200, chunks, gate=gate, block_after=2)
    http = httpx.AsyncClient(transport=transport, base_url="http://o.test")
    client = OllamaClient("http://o.test", client=http)
    seen: list[PullProgress] = []

    async def run():
        async with http:
            task = _asyncio.create_task(client.pull_model("m", on_progress=seen.append))
            # Let the first records land, then cancel mid-download.
            for _ in range(100):
                if seen and seen[-1].total_bytes is not None:
                    break
                await _asyncio.sleep(0.01)
            task.cancel()
            with pytest.raises(_asyncio.CancelledError):
                await task

    asyncio.run(run())
    assert seen, "progress was observed before cancellation"
    assert seen[-1].status != "success"


# ── Resource checks ──────────────────────────────────────────────────


def test_models_dir_is_a_real_path_on_this_machine():
    path = ollama_models_dir()
    assert path
    assert not path.startswith("/nonexistent")


def test_disk_status_reports_real_free_space():
    status = disk_status()
    assert status.available, status.error
    assert status.free_bytes > 0
    assert status.total_bytes >= status.free_bytes


def test_disk_status_walks_up_to_an_existing_ancestor():
    status = disk_status(ollama_models_dir())
    assert status.available, status.error
    assert status.free_bytes > 0


def test_installed_ram_is_reported_as_a_real_value():
    ram = installed_ram_bytes()
    assert ram is not None
    assert ram > 0


def test_sufficient_space_and_ram_do_not_block(monkeypatch):
    # Free space is re-read on every call, so a test that compares two live
    # readings races with anything else writing to the disk. Pin both.
    monkeypatch.setattr(
        "backend.app.ai.resources.disk_status",
        lambda path=None: DiskStatus(path="C:/fake", total_bytes=10**12, free_bytes=10**11),
    )
    monkeypatch.setattr(
        "backend.app.ai.resources.installed_ram_bytes", lambda: 16 * 1024**3,
    )
    result = check_for_model_download(10**10)
    assert result.blocking is False
    assert result.code is None
    assert result.guidance is None


def test_insufficient_disk_space_blocks_with_an_actionable_message(monkeypatch):
    monkeypatch.setattr(
        "backend.app.ai.resources.disk_status",
        lambda path=None: DiskStatus(path="C:/fake", total_bytes=10**12, free_bytes=5 * 1024**3),
    )
    monkeypatch.setattr(
        "backend.app.ai.resources.installed_ram_bytes", lambda: 16 * 1024**3,
    )
    required = 10 * 1024**3   # 10 GiB wanted, 5 GiB free
    result = check_for_model_download(required)
    assert result.blocking is True
    assert result.code == "INSUFFICIENT_DISK_SPACE"
    assert "free space" in result.guidance
    assert "C:/fake" in result.guidance
    # The shortfall is a real figure, not a placeholder.
    assert "5.0 GB" in result.guidance


def test_low_ram_blocks_before_a_download_starts(monkeypatch):
    monkeypatch.setattr(
        "backend.app.ai.resources.disk_status",
        lambda path=None: DiskStatus(path="C:/fake", total_bytes=10**12, free_bytes=10**11),
    )
    monkeypatch.setattr(
        "backend.app.ai.resources.installed_ram_bytes", lambda: 2 * 1024**3,
    )
    result = check_for_model_download(10**10)
    assert result.blocking is True
    assert result.code == "INSUFFICIENT_MEMORY"
    assert MIN_DOWNLOAD_RAM_BYTES == 4 * 1024**3


def test_the_preflight_runs_against_this_machine():
    # No mocking: whatever this host reports must come back well-formed,
    # and a size that fits in free space must never be rejected.
    status = disk_status()
    result = check_for_model_download(1)
    assert result.disk.path == status.path
    assert result.ram_bytes == installed_ram_bytes()
    assert result.blocking is False


def test_unknown_required_size_does_not_block():
    result = check_for_model_download(None)
    assert result.blocking is False
    assert result.code is None


def test_low_ram_blocks_before_a_download_starts(monkeypatch):
    monkeypatch.setattr(
        "backend.app.ai.resources.installed_ram_bytes",
        lambda: MIN_DOWNLOAD_RAM_BYTES - 1,
    )
    result = check_for_model_download(None)
    assert result.blocking is True
    assert result.code == "INSUFFICIENT_MEMORY"
    assert result.ram_sufficient is False


def test_unreadable_ram_is_reported_as_uncertain_not_as_failure(monkeypatch):
    monkeypatch.setattr("backend.app.ai.resources.installed_ram_bytes", lambda: None)
    result = check_for_model_download(None)
    assert result.blocking is False
    assert result.ram_sufficient is None


def test_unreadable_disk_is_blocking(monkeypatch):
    broken = DiskStatus(path="X:", total_bytes=0, free_bytes=0, error="OSError")
    monkeypatch.setattr("backend.app.ai.resources.disk_status", lambda *a, **k: broken)
    result = check_for_model_download(1)
    assert result.blocking is True
    assert result.code == "DISK_CHECK_FAILED"


def test_human_bytes_formats_consistently():
    assert human_bytes(None) == "unknown size"
    assert human_bytes(512) == "512 B"
    assert human_bytes(2048) == "2.0 KB"
    assert human_bytes(5 * 1024 ** 3) == "5.0 GB"
    assert human_bytes(3 * 1024 ** 4) == "3.0 TB"


def test_model_size_uses_the_real_reported_size():
    async def tags():
        return {"models": [
            {"name": "qwen3:4b", "size": 2_500_000_000,
             "details": {"parameter_size": "4B", "quantization_level": "Q4_K_M"}},
            {"name": "other:1b", "size": 100, "details": {}},
        ]}

    client = OllamaClient("http://o.test")
    client.health = tags  # type: ignore[method-assign]
    assert asyncio.run(client.model_size("qwen3:4b")) == 2_500_000_000
    assert asyncio.run(client.model_size("absent:4b")) is None


def test_list_models_reports_names_and_sizes_without_invention():
    async def tags():
        return {"models": [{"name": "qwen3:4b", "size": 42,
                            "details": {"parameter_size": "4B"}}]}

    client = OllamaClient("http://o.test")
    client.health = tags  # type: ignore[method-assign]
    assert asyncio.run(client.list_models()) == [
        {"name": "qwen3:4b", "size_bytes": 42,
         "parameter_size": "4B", "quantization": ""},
    ]
