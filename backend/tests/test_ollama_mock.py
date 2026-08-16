import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import httpx
import asyncio
from backend.app.ai.ollama_client import OllamaClient, OllamaUnavailable, InferenceMetrics
from backend.app.ai.service import AIService
from backend.app.schemas import Email, EmailAnalysis, Category, Priority

def test_ollama_client_sends_correct_payload():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": '{"french": "bonjour"}',
        "model": "qwen3:4b",
        "done": True,
        "done_reason": "stop"
    }
    mock_client.post.return_value = mock_response

    client = OllamaClient("http://fakeurl", client=mock_client)
    schema = {"type": "object", "properties": {"french": {"type": "string"}}, "required": ["french"]}
    
    res, metrics = asyncio.run(client.generate("qwen3:4b", "Translate hello", schema))

    assert res == '{"french": "bonjour"}'
    mock_client.post.assert_called_once_with(
        "http://fakeurl/api/generate",
        json={
            "model": "qwen3:4b",
            "prompt": "Translate hello",
            "format": schema,
            "stream": False,
            "think": False,
            "keep_alive": "30m",
            "options": {"temperature": 0.0}
        }
    )

def test_ollama_client_empty_response():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": "",
        "model": "qwen3:4b",
        "done": True,
        "done_reason": "stop"
    }
    mock_client.post.return_value = mock_response

    client = OllamaClient("http://fakeurl", client=mock_client)
    res, metrics = asyncio.run(client.generate("qwen3:4b", "Translate hello", {}))
    assert res == ""

def test_ollama_client_http_error():
    mock_client = AsyncMock()
    mock_client.post.side_effect = httpx.HTTPError("Inference failed")

    client = OllamaClient("http://fakeurl", client=mock_client)
    with pytest.raises(OllamaUnavailable):
        asyncio.run(client.generate("qwen3:4b", "Translate hello", {}))

def test_ai_service_analyze_email_success():
    mock_client = AsyncMock()
    analysis_data = {
        "short_summary": "Test Summary",
        "category": "work",
        "priority": "high",
        "priority_score": 80,
        "reason_for_priority": "Important",
        "needs_reply": True,
        "action_items": [],
        "deadlines": [],
        "important_entities": [],
        "important_details": []
    }
    
    client = OllamaClient("http://fakeurl", client=mock_client)
    service = AIService(client, "qwen3:4b")

    with patch.object(client, 'generate', return_value=(json.dumps(analysis_data), InferenceMetrics())) as mock_gen:
        email = Email(id="1", sender="a@b.com", subject="Subj", body="Body")
        res, metrics = asyncio.run(service.analyze_email(email))
        assert isinstance(res, EmailAnalysis)
        assert res.short_summary == "Test Summary"
        assert res.priority == Priority.high
        mock_gen.assert_called_once()
