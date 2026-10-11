"""Ollama HTTP client with performance metrics, error classification, and model lifecycle management."""
import codecs
import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Callable, Iterable, Iterator

import httpx

logger = logging.getLogger("alfred.ai.ollama")


class OllamaUnavailable(Exception):
    """Ollama service is not reachable."""
    pass

class OllamaTimeout(Exception):
    """Ollama request timed out."""
    pass

class OllamaInvalidResponse(Exception):
    """Ollama returned unparseable or empty response."""
    pass

class OllamaModelMissing(Exception):
    """Requested model is not available in Ollama."""
    pass

class OllamaPullFailed(Exception):
    """Ollama rejected or aborted a model pull."""
    pass

class OllamaInsufficientSpace(Exception):
    """Free space ran out (or was already too low) for the announced download."""

    def __init__(self, required_bytes: int, free_bytes: int):
        super().__init__(
            f"model download needs {required_bytes} bytes but only "
            f"{free_bytes} are free"
        )
        self.required_bytes = required_bytes
        self.free_bytes = free_bytes


class NdjsonStreamDecoder:
    """Incremental decoder for a newline-delimited JSON byte stream.

    Ollama's streaming endpoints write one JSON object per line, and a line
    routinely arrives split across network chunks. This holds the incomplete
    tail until its newline appears, so no record is ever emitted half-formed.

    A malformed line is dropped and logged rather than aborting the stream:
    one bad record must not discard a download that is otherwise healthy.
    """

    def __init__(self) -> None:
        self._buf = ""
        self._decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        self._malformed = 0

    @property
    def malformed_count(self) -> int:
        return self._malformed

    def feed(self, chunk: bytes) -> list[dict]:
        """Decode one network chunk; return every record it completed."""
        self._buf += self._decoder.decode(chunk)
        return self._drain(final=False)

    def flush(self) -> list[dict]:
        """Emit any record whose final newline never arrived."""
        self._buf += self._decoder.decode(b"", final=True)
        return self._drain(final=True)

    def _drain(self, final: bool) -> list[dict]:
        records: list[dict] = []
        while True:
            idx = self._buf.find("\n")
            if idx < 0:
                break
            line, self._buf = self._buf[:idx], self._buf[idx + 1:]
            record = _parse_record(line, self)
            if record is not None:
                records.append(record)
        if final and self._buf.strip():
            record = _parse_record(self._buf, self)
            self._buf = ""
            if record is not None:
                records.append(record)
        return records


def _parse_record(line: str, decoder: NdjsonStreamDecoder | None = None) -> dict | None:
    stripped = line.strip()
    if not stripped:
        return None
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        if decoder is not None:
            decoder._malformed += 1
        logger.warning("ollama_ndjson_malformed_dropped")
        return None
    if not isinstance(parsed, dict):
        if decoder is not None:
            decoder._malformed += 1
        logger.warning("ollama_ndjson_non_object_dropped")
        return None
    return parsed


def iter_ndjson_records(chunks: Iterable[bytes]) -> Iterator[dict]:
    """Convenience wrapper over `NdjsonStreamDecoder` for plain byte chunks."""
    decoder = NdjsonStreamDecoder()
    for chunk in chunks:
        yield from decoder.feed(chunk)
    yield from decoder.flush()


@dataclass(frozen=True)
class PullProgress:
    """One progress observation from a model pull.

    `total_bytes` is None until Ollama has announced at least one layer's
    size; it is never estimated. Per-layer values refer to `digest`, or are
    None when the record carried no layer detail.
    """

    status: str
    completed_bytes: int
    total_bytes: int | None
    digest: str | None
    layer_completed: int | None
    layer_total: int | None

    @property
    def fraction(self) -> float | None:
        """Fraction downloaded so far, or None when the total is unknown."""
        if not self.total_bytes:
            return None
        return min(1.0, self.completed_bytes / self.total_bytes)


class LayerProgressAggregator:
    """Tracks per-layer byte counts without double-counting.

    Ollama emits one record per layer update, keyed by digest, repeating the
    same digest many times as that layer downloads. Summing every record
    would count the same layer repeatedly, so the latest value per digest is
    kept and only new digests change the announced total.
    """

    def __init__(self) -> None:
        self._layers: dict[str, tuple[int | None, int | None]] = {}
        self._status = ""

    def observe(self, record: dict) -> PullProgress:
        status = str(record.get("status", ""))
        if status:
            self._status = status

        digest = record.get("digest")
        layer_total = record.get("total")
        layer_completed = record.get("completed")

        if isinstance(digest, str) and digest:
            total = layer_total if isinstance(layer_total, int) else None
            completed = layer_completed if isinstance(layer_completed, int) else None
            self._layers[digest] = (total, completed)

        totals = [t for t, _ in self._layers.values() if t]
        completeds = [c for _, c in self._layers.values() if c]
        return PullProgress(
            status=self._status,
            completed_bytes=sum(completeds),
            total_bytes=sum(totals) if totals else None,
            digest=digest if isinstance(digest, str) and digest else None,
            layer_total=layer_total if isinstance(layer_total, int) else None,
            layer_completed=layer_completed if isinstance(layer_completed, int) else None,
        )

    @property
    def announced_total(self) -> int | None:
        """Total bytes Ollama has announced so far, or None."""
        totals = [t for t, _ in self._layers.values() if t]
        return sum(totals) if totals else None


class InferenceMetrics:
    """Container for Ollama response performance metrics."""
    __slots__ = ('total_ms', 'load_ms', 'prompt_eval_ms', 'eval_ms',
                 'prompt_tokens', 'output_tokens')
    
    def __init__(self, total_ms=0.0, load_ms=0.0, prompt_eval_ms=0.0, eval_ms=0.0,
                 prompt_tokens=0, output_tokens=0):
        self.total_ms = total_ms
        self.load_ms = load_ms
        self.prompt_eval_ms = prompt_eval_ms
        self.eval_ms = eval_ms
        self.prompt_tokens = prompt_tokens
        self.output_tokens = output_tokens


class OllamaClient:
    """Async HTTP client for Ollama's /api/generate endpoint.
    
    Features:
    - Model preloading with keep_alive
    - Performance metrics extraction
    - Classified error types
    - Configurable timeouts
    """
    
    def __init__(self, base_url: str, client: httpx.AsyncClient | None = None,
                 default_timeout: float = 120.0, keep_alive: str = "30m"):
        self.base_url = base_url.rstrip('/')
        self.client = client or httpx.AsyncClient(timeout=default_timeout)
        self.keep_alive = keep_alive
        self._model_loaded = False
    
    async def health(self) -> dict:
        """Check if Ollama is reachable and return available models."""
        try:
            r = await self.client.get(f'{self.base_url}/api/tags')
            r.raise_for_status()
            return r.json()
        except httpx.TimeoutException as e:
            raise OllamaTimeout('Ollama health check timed out.') from e
        except httpx.HTTPError as e:
            raise OllamaUnavailable('Ollama is not currently reachable.') from e

    async def list_models(self) -> list[dict]:
        """Local models with their real sizes, as Ollama reports them.

        Returns `{"name", "size_bytes", "parameter_size", "quantization"}`
        per model. Sizes come from `/api/tags`; nothing is inferred.
        """
        data = await self.health()
        out: list[dict] = []
        for model in data.get("models", []):
            name = str(model.get("name", ""))
            if not name:
                continue
            details = model.get("details") or {}
            size = model.get("size")
            out.append({
                "name": name,
                "size_bytes": int(size) if isinstance(size, int) else None,
                "parameter_size": str(details.get("parameter_size", "") or ""),
                "quantization": str(details.get("quantization_level", "") or ""),
            })
        return out

    async def model_size(self, model: str) -> int | None:
        """Real on-disk size of a locally installed model, or None if absent.

        Ollama does not publish registry sizes through its local API, so a
        model that has never been pulled has no knowable size here. That is
        reported as None rather than filled in with an estimate.
        """
        for entry in await self.list_models():
            name = entry["name"]
            if name == model or name == f"{model}:latest" or f"{model}:latest" == name:
                if entry["size_bytes"] is not None:
                    return entry["size_bytes"]
        return None

    async def pull_model(
        self,
        model: str,
        on_progress: Callable[[PullProgress], None] | None = None,
        check_space: Callable[[int | None], None] | None = None,
    ) -> PullProgress:
        """Download a model, streaming real per-layer byte progress.

        `on_progress` is called synchronously with each observation, before
        the next network read, so a caller can publish progress without
        racing its own consumer.

        `check_space` is invoked with the announced total as soon as Ollama
        reports layer sizes — which happens before layer bodies finish
        transferring — and may raise `OllamaInsufficientSpace` to abort the
        download before it fills the disk.

        Cancellation: awaiting this coroutine and then cancelling the task
        closes the HTTP stream, which is what makes Ollama abandon the pull.
        Completed layers stay on disk, so a later pull resumes at layer
        granularity rather than restarting from zero.

        Raises:
            OllamaUnavailable: service unreachable
            OllamaTimeout: the request timed out
            OllamaPullFailed: Ollama returned an error record or a bad status
            OllamaInsufficientSpace: aborted by the space preflight
        """
        aggregator = LayerProgressAggregator()
        last = PullProgress(status="starting", completed_bytes=0,
                            total_bytes=None, digest=None,
                            layer_completed=None, layer_total=None)
        space_state = [False]  # mutated: has the space preflight run yet?

        def handle(record: dict) -> PullProgress:
            nonlocal last
            if "error" in record:
                raise OllamaPullFailed(str(record["error"]))
            last = aggregator.observe(record)
            if on_progress is not None:
                on_progress(last)
            if not space_state[0] and last.total_bytes is not None:
                # The announced total is now known; run the space preflight
                # before more layer bytes move.
                space_state[0] = True
                if check_space is not None:
                    check_space(last.total_bytes)
            return last

        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/pull",
                json={"name": model, "stream": True},
                # A model download is long-lived; the client-wide read
                # timeout must not sever it mid-transfer.
                timeout=httpx.Timeout(None, read=300.0, connect=10.0),
            ) as response:
                if response.status_code >= 400:
                    body = await response.aread()
                    raise OllamaPullFailed(
                        f"pull rejected with HTTP {response.status_code}: "
                        f"{body.decode('utf-8', 'replace')[:300]}"
                    )

                decoder = NdjsonStreamDecoder()
                async for raw in response.aiter_bytes():
                    for record in decoder.feed(raw):
                        handle(record)
                for record in decoder.flush():
                    handle(record)
        except httpx.TimeoutException as e:
            raise OllamaTimeout(f"model pull timed out for {model}.") from e
        except httpx.HTTPError as e:
            raise OllamaUnavailable(f"model pull failed for {model}.") from e

        if last.status != "success":
            raise OllamaPullFailed(
                f"Ollama finished the pull stream without reporting success "
                f"(last status: {last.status or 'none'})"
            )
        return last


    
    async def preload_model(self, model: str):
        """Preload a model into VRAM/RAM to avoid cold-start latency on first inference."""
        try:
            r = await self.client.post(
                f'{self.base_url}/api/generate',
                json={'model': model, 'keep_alive': -1},
                timeout=180.0  # Model loading can take time
            )
            r.raise_for_status()
            self._model_loaded = True
        except httpx.HTTPError:
            pass  # Non-fatal: first inference will just be slower
    
    async def generate(self, model: str, prompt: str, schema=None,
                       temperature: float = 0.0) -> tuple[str, InferenceMetrics]:
        """Generate a response from Ollama.
        
        Returns:
            tuple of (response_text, InferenceMetrics)
        
        Raises:
            OllamaUnavailable: Service unreachable
            OllamaTimeout: Request timed out
            OllamaInvalidResponse: Empty or unparseable response
            OllamaModelMissing: Model not found
        """
        payload = {
            'model': model,
            'prompt': prompt,
            'stream': False,
            'think': False,
            'keep_alive': self.keep_alive,
            'options': {'temperature': temperature}
        }
        if schema:
            payload['format'] = schema
        
        try:
            r = await self.client.post(f'{self.base_url}/api/generate', json=payload)
            
            # Check for model not found
            if r.status_code == 404:
                raise OllamaModelMissing(f'Model "{model}" is not available in Ollama.')
            
            r.raise_for_status()
            data = r.json()
            
            # Extract response text
            response_text = data.get('response', '')
            
            # Strip any thinking tags that leaked through
            clean_text = re.sub(
                r'<(think|thinking)>.*?</\1>', '', response_text,
                flags=re.IGNORECASE | re.DOTALL
            ).strip()
            
            if not clean_text and schema:
                raise OllamaInvalidResponse(
                    f'Ollama returned empty response for structured output. '
                    f'Model: {model}. This may indicate a compatibility issue with the model.'
                )
            
            # Extract performance metrics (durations are in nanoseconds)
            metrics = InferenceMetrics(
                total_ms=data.get('total_duration', 0) / 1_000_000,
                load_ms=data.get('load_duration', 0) / 1_000_000,
                prompt_eval_ms=data.get('prompt_eval_duration', 0) / 1_000_000,
                eval_ms=data.get('eval_duration', 0) / 1_000_000,
                prompt_tokens=data.get('prompt_eval_count', 0),
                output_tokens=data.get('eval_count', 0),
            )
            
            return clean_text, metrics
            
        except OllamaModelMissing:
            raise
        except OllamaInvalidResponse:
            raise
        except httpx.TimeoutException as e:
            raise OllamaTimeout(
                f'Ollama inference timed out after {self.client.timeout.read}s. '
                f'Model: {model}. Try a shorter prompt or check GPU resources.'
            ) from e
        except httpx.HTTPError as e:
            raise OllamaUnavailable('Ollama inference failed.') from e
