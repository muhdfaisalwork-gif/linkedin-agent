import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

from .providers import (
    BaseLLMProvider,
    OllamaProvider,
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    OpenRouterProvider,
    CustomOpenAICompatibleProvider
)

def _get_db_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """Helper to fetch setting directly from database if available."""
    try:
        from core.db.database import get_connection
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key = ? LIMIT 1", (key,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception:
        pass
    return default

class UniversalLLMClient:
    """
    Universal Multi-Model Provider Client:
    Seamlessly routes requests to Local Ollama, OpenAI, Anthropic Claude,
    Google Gemini, or OpenRouter based on user configuration in Settings / DB.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self._explicit_provider = provider
        self._explicit_api_key = api_key
        self._explicit_model = model
        self._explicit_base_url = base_url
        self._providers_cache: Dict[str, BaseLLMProvider] = {}

    @property
    def active_provider_name(self) -> str:
        if self._explicit_provider:
            return self._explicit_provider.lower()
        db_val = _get_db_setting("LLM_PROVIDER")
        env_val = os.getenv("LLM_PROVIDER")
        provider = (db_val or env_val or "openrouter").lower()
        return provider

    @property
    def current_model(self) -> str:
        provider = self.active_provider_name
        if self._explicit_model:
            return self._explicit_model
        if provider == "ollama":
            return _get_db_setting("OLLAMA_MODEL") or os.getenv("OLLAMA_MODEL") or "llama3.2:latest"
        elif provider == "openai":
            return _get_db_setting("OPENAI_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o"
        elif provider == "anthropic":
            return _get_db_setting("ANTHROPIC_MODEL") or os.getenv("ANTHROPIC_MODEL") or "claude-3-5-sonnet-20241022"
        elif provider == "gemini":
            return _get_db_setting("GEMINI_MODEL") or os.getenv("GEMINI_MODEL") or "gemini-2.0-flash"
        elif provider == "custom":
            return _get_db_setting("CUSTOM_MODEL") or os.getenv("CUSTOM_MODEL") or "local-model"
        else:
            return _get_db_setting("OPENROUTER_MODEL") or os.getenv("OPENROUTER_MODEL") or "openrouter/free"

    @property
    def api_key(self) -> Optional[str]:
        provider = self.active_provider_name
        if self._explicit_api_key:
            return self._explicit_api_key
        if provider == "openai":
            return _get_db_setting("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        elif provider == "anthropic":
            return _get_db_setting("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        elif provider == "gemini":
            return _get_db_setting("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        elif provider == "custom":
            return _get_db_setting("CUSTOM_API_KEY") or os.getenv("CUSTOM_API_KEY")
        elif provider == "ollama":
            return None
        else:
            return _get_db_setting("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")

    def get_provider_instance(self, provider_name: Optional[str] = None) -> BaseLLMProvider:
        name = (provider_name or self.active_provider_name).lower()
        model = self.current_model

        if name == "ollama":
            base_url = self._explicit_base_url or _get_db_setting("OLLAMA_BASE_URL") or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            return OllamaProvider(base_url=base_url, model=model)
        elif name == "openai":
            key = self._explicit_api_key or _get_db_setting("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
            return OpenAIProvider(api_key=key, model=model)
        elif name == "anthropic":
            key = self._explicit_api_key or _get_db_setting("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
            return AnthropicProvider(api_key=key, model=model)
        elif name == "gemini":
            key = self._explicit_api_key or _get_db_setting("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
            return GeminiProvider(api_key=key, model=model)
        elif name == "custom":
            base_url = self._explicit_base_url or _get_db_setting("CUSTOM_BASE_URL") or os.getenv("CUSTOM_BASE_URL")
            key = self._explicit_api_key or _get_db_setting("CUSTOM_API_KEY") or os.getenv("CUSTOM_API_KEY")
            return CustomOpenAICompatibleProvider(base_url=base_url, api_key=key, model=model)
        else:
            key = self._explicit_api_key or _get_db_setting("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
            return OpenRouterProvider(api_key=key, model=model)

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Delegates chat completion to the currently active provider."""
        provider = self.get_provider_instance()
        return provider.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format
        )

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Convenience text generation."""
        provider = self.get_provider_instance()
        return provider.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )

    def get_available_free_models(self) -> List[str]:
        """Returns free models available via OpenRouter."""
        return OpenRouterProvider().list_models()

    def list_models_for_active_provider(self) -> List[str]:
        """Returns list of models for the active provider."""
        return self.get_provider_instance().list_models()

# Backwards compatibility alias: Every skill importing OpenRouterClient continues to work seamlessly!
class OpenRouterClient(UniversalLLMClient):
    """Backwards-compatible alias for UniversalLLMClient."""
    pass

def get_llm_client() -> UniversalLLMClient:
    return UniversalLLMClient()
