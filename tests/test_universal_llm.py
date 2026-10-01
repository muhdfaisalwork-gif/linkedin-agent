import os
import pytest
from unittest.mock import patch, MagicMock

from core.llm.client import UniversalLLMClient, OpenRouterClient
from core.llm.providers.ollama import OllamaProvider
from core.llm.providers.openai import OpenAIProvider
from core.llm.providers.anthropic import AnthropicProvider
from core.llm.providers.gemini import GeminiProvider
from core.llm.providers.openrouter import OpenRouterProvider
from core.llm.providers.custom import CustomOpenAICompatibleProvider

def test_ollama_provider_list_models_and_properties():
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "models": [
                {"name": "qwen2.5:latest"},
                {"name": "llama3.2:latest"}
            ]
        }
        provider = OllamaProvider(base_url="http://localhost:11434")
        assert provider.name == "ollama"
        assert provider.base_url == "http://localhost:11434"
        models = provider.list_models()
        assert "qwen2.5:latest" in models
        assert "llama3.2:latest" in models
        assert provider.model == "qwen2.5:latest"

def test_ollama_provider_chat_completion_with_think_stripping():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "message": {
                "role": "assistant",
                "content": "<think>Thinking deeply about LinkedIn...</think>Here is the high-converting post draft."
            }
        }
        provider = OllamaProvider(base_url="http://localhost:11434", model="deepseek-r1:8b")
        res = provider.chat_completion([{"role": "user", "content": "Write post"}])
        assert res["content"] == "Here is the high-converting post draft."
        assert res["model_used"] == "deepseek-r1:8b"
        assert res["provider"] == "ollama"

def test_openai_provider():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [
                {"message": {"content": "OpenAI generated content"}}
            ]
        }
        provider = OpenAIProvider(api_key="sk-test-fake", model="gpt-4o")
        assert provider.name == "openai"
        assert "gpt-4o" in provider.list_models()
        res = provider.chat_completion([{"role": "user", "content": "Hello"}])
        assert res["content"] == "OpenAI generated content"
        assert res["provider"] == "openai"

def test_anthropic_provider():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "content": [
                {"type": "text", "text": "Anthropic Claude generated response"}
            ]
        }
        provider = AnthropicProvider(api_key="sk-ant-test-fake", model="claude-3-5-sonnet-20241022")
        assert provider.name == "anthropic"
        assert "claude-3-5-sonnet-20241022" in provider.list_models()
        res = provider.chat_completion([
            {"role": "system", "content": "Act as an expert"},
            {"role": "user", "content": "Draft post"}
        ])
        assert res["content"] == "Anthropic Claude generated response"
        assert res["provider"] == "anthropic"

def test_gemini_provider():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [
                {"message": {"content": "Google Gemini generated draft"}}
            ]
        }
        provider = GeminiProvider(api_key="AIzaSyTestFake", model="gemini-2.0-flash")
        assert provider.name == "gemini"
        assert "gemini-2.0-flash" in provider.list_models()
        res = provider.chat_completion([{"role": "user", "content": "Draft hook"}])
        assert res["content"] == "Google Gemini generated draft"
        assert res["provider"] == "gemini"

def test_universal_llm_client_routing():
    # Explicit provider routing
    client_ollama = UniversalLLMClient(provider="ollama", model="qwen2.5:latest")
    assert client_ollama.active_provider_name == "ollama"
    assert client_ollama.current_model == "qwen2.5:latest"

    client_claude = UniversalLLMClient(provider="anthropic", api_key="test-key", model="claude-3-5-haiku-20241022")
    assert client_claude.active_provider_name == "anthropic"
    assert client_claude.current_model == "claude-3-5-haiku-20241022"

    client_gemini = UniversalLLMClient(provider="gemini", api_key="test-key", model="gemini-2.0-flash")
    assert client_gemini.active_provider_name == "gemini"
    assert client_gemini.current_model == "gemini-2.0-flash"

def test_openrouter_backwards_compatibility():
    # Ensure OpenRouterClient is an instance of UniversalLLMClient
    client = OpenRouterClient()
    assert isinstance(client, UniversalLLMClient)
    assert hasattr(client, "chat_completion")
    assert hasattr(client, "generate_text")

def test_openai_empty_choices_handling():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"choices": []}
        provider = OpenAIProvider(api_key="sk-test", model="gpt-4o")
        with pytest.raises(RuntimeError, match="no choices"):
            provider.chat_completion([{"role": "user", "content": "Hi"}])

def test_gemini_blocked_prompt_handling():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [],
            "promptFeedback": {"blockReason": "SAFETY"}
        }
        provider = GeminiProvider(api_key="AIzaSyTest", model="gemini-2.0-flash")
        with pytest.raises(RuntimeError, match="blocked prompt: SAFETY"):
            provider.chat_completion([{"role": "user", "content": "Hi"}])

def test_custom_empty_choices_handling():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"choices": []}
        provider = CustomOpenAICompatibleProvider(base_url="http://localhost:1234/v1")
        with pytest.raises(RuntimeError, match="no choices"):
            provider.chat_completion([{"role": "user", "content": "Hi"}])

def test_ollama_unclosed_think_tag_stripping():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "message": {
                "role": "assistant",
                "content": "<think>Cut off mid-reasoning without closing tag"
            }
        }
        provider = OllamaProvider(base_url="http://localhost:11434")
        res = provider.chat_completion([{"role": "user", "content": "Hi"}])
        assert res["content"] == ""

def test_universal_llm_per_provider_model_lookup():
    client = UniversalLLMClient()
    gemini_prov = client.get_provider_instance("gemini")
    assert gemini_prov.name == "gemini"
    assert "gemini" in gemini_prov.model.lower()

    anthropic_prov = client.get_provider_instance("anthropic")
    assert anthropic_prov.name == "anthropic"
    assert "claude" in anthropic_prov.model.lower()
