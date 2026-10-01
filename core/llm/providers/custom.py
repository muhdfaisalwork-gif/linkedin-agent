import os
import requests
from typing import List, Dict, Any, Optional
from .base import BaseLLMProvider

class CustomOpenAICompatibleProvider(BaseLLMProvider):
    """
    Custom OpenAI-Compatible Provider:
    Connects to any endpoint implementing /v1/chat/completions (LM Studio, vLLM, DeepSeek, Groq, etc.).
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, model: Optional[str] = None):
        self._base_url = (base_url or os.getenv("CUSTOM_BASE_URL", "http://localhost:1234/v1")).rstrip("/")
        self._api_key = api_key or os.getenv("CUSTOM_API_KEY", "")
        self._model = model or os.getenv("CUSTOM_MODEL", "local-model")

    @property
    def name(self) -> str:
        return "custom"

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def model(self) -> str:
        return self._model

    def list_models(self) -> List[str]:
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            res = requests.get(f"{self.base_url}/models", headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                return [m["id"] for m in data.get("data", []) if "id" in m]
        except Exception:
            pass
        return [self.model]

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        if response_format:
            payload["response_format"] = response_format

        try:
            res = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            if res.status_code == 200:
                data = res.json()
                choice = data["choices"][0]["message"]
                content = choice.get("content", "")
                return {
                    "content": content,
                    "model_used": self.model,
                    "provider": "custom",
                    "raw": data
                }
            else:
                raise RuntimeError(f"Custom endpoint returned HTTP {res.status_code}: {res.text[:200]}")
        except Exception as e:
            raise RuntimeError(f"Custom LLM endpoint error: {str(e)}")
