import os
import requests
from typing import List, Dict, Any, Optional
from .base import BaseLLMProvider

class OpenAIProvider(BaseLLMProvider):
    """
    Direct OpenAI Provider:
    Connects to official OpenAI API using OPENAI_API_KEY.
    """

    DEFAULT_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "o3-mini",
        "o1",
        "gpt-4-turbo"
    ]

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        self._api_key = api_key
        self._model = model
        self._base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")

    @property
    def name(self) -> str:
        return "openai"

    @property
    def api_key(self) -> Optional[str]:
        return self._api_key or os.getenv("OPENAI_API_KEY")

    @property
    def model(self) -> str:
        return self._model or os.getenv("OPENAI_MODEL", "gpt-4o")

    def list_models(self) -> List[str]:
        return self.DEFAULT_MODELS

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        key = self.api_key
        if not key:
            raise ValueError("OpenAI API Key is missing. Please enter your key in Settings or set OPENAI_API_KEY.")

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

        target_model = self.model
        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": messages
        }

        # Reasoning models (o1, o3-mini) do not accept custom temperature
        if not target_model.startswith("o1") and not target_model.startswith("o3"):
            payload["temperature"] = temperature
            payload["max_tokens"] = max_tokens
        else:
            payload["max_completion_tokens"] = max_tokens

        if response_format:
            payload["response_format"] = response_format

        try:
            res = requests.post(
                f"{self._base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            if res.status_code == 200:
                data = res.json()
                choices = data.get("choices", [])
                if not choices:
                    raise RuntimeError(f"OpenAI returned no choices: {data}")
                choice = choices[0].get("message", {})
                content = choice.get("content") or choice.get("refusal") or ""
                return {
                    "content": content,
                    "model_used": target_model,
                    "provider": "openai",
                    "raw": data
                }
            else:
                raise RuntimeError(f"OpenAI returned HTTP {res.status_code}: {res.text[:200]}")
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
