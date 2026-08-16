"""Ollama HTTP client with performance metrics, error classification, and model lifecycle management."""
import httpx
import re
import time


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
