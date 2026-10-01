import os
import requests
from typing import List, Dict, Any, Optional
from .base import BaseLLMProvider

class GeminiProvider(BaseLLMProvider):
    """
    Direct Google Gemini Provider:
    Connects to Google Generative Language API using GEMINI_API_KEY.
    Uses the official OpenAI-compatible endpoint for maximum speed and compatibility.
    """

    DEFAULT_MODELS = [
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "gemini-1.5-flash"
    ]

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self._api_key = api_key
        self._model = model

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def api_key(self) -> Optional[str]:
        return self._api_key or os.getenv("GEMINI_API_KEY")

    @property
    def model(self) -> str:
        return self._model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

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
            raise ValueError("Google Gemini API Key is missing. Please enter your key in Settings or set GEMINI_API_KEY.")

        # Google's OpenAI-compatible endpoint
        endpoint = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

        target_model = self.model
        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        if response_format:
            payload["response_format"] = response_format

        try:
            res = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=60
            )
            if res.status_code == 200:
                data = res.json()
                choices = data.get("choices", [])
                if not choices:
                    feedback = data.get("promptFeedback", {})
                    block_reason = feedback.get("blockReason")
                    if block_reason:
                        raise RuntimeError(f"Google Gemini blocked prompt: {block_reason}")
                    raise RuntimeError(f"Google Gemini returned no choices: {data}")
                choice = choices[0].get("message", {})
                content = choice.get("content", "")
                return {
                    "content": content,
                    "model_used": target_model,
                    "provider": "gemini",
                    "raw": data
                }
            else:
                raise RuntimeError(f"Google Gemini returned HTTP {res.status_code}: {res.text[:200]}")
        except Exception as e:
            raise RuntimeError(f"Google Gemini API error: {str(e)}")
