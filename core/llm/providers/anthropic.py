import os
import requests
from typing import List, Dict, Any, Optional
from .base import BaseLLMProvider

class AnthropicProvider(BaseLLMProvider):
    """
    Direct Anthropic Claude Provider:
    Connects to official Anthropic API using ANTHROPIC_API_KEY.
    """

    DEFAULT_MODELS = [
        "claude-3-7-sonnet-20250219",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229"
    ]

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self._api_key = api_key
        self._model = model

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def api_key(self) -> Optional[str]:
        return self._api_key or os.getenv("ANTHROPIC_API_KEY")

    @property
    def model(self) -> str:
        return self._model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

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
            raise ValueError("Anthropic API Key is missing. Please enter your key in Settings or set ANTHROPIC_API_KEY.")

        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        # Extract system prompt if present
        system_content = None
        claude_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                system_content = content
            else:
                claude_messages.append({"role": role, "content": content})

        if not claude_messages:
            claude_messages.append({"role": "user", "content": "Hello"})

        target_model = self.model
        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": claude_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        if system_content:
            payload["system"] = system_content

        try:
            res = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=60
            )
            if res.status_code == 200:
                data = res.json()
                content_blocks = data.get("content", [])
                text = "".join([b.get("text", "") for b in content_blocks if b.get("type") == "text"])
                return {
                    "content": text,
                    "model_used": target_model,
                    "provider": "anthropic",
                    "raw": data
                }
            else:
                raise RuntimeError(f"Anthropic returned HTTP {res.status_code}: {res.text[:200]}")
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")
