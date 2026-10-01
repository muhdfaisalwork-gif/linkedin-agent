import os
import requests
from typing import List, Dict, Any, Optional
from .base import BaseLLMProvider

class OllamaProvider(BaseLLMProvider):
    """
    Local Ollama Provider:
    Connects to local Ollama instance (default: http://localhost:11434)
    Runs 100% locally and offline on user's machine with zero API keys.
    """

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self._base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self._model = model or os.getenv("OLLAMA_MODEL")

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def model(self) -> str:
        if self._model:
            return self._model
        # Fallback to first installed model or llama3.2
        installed = self.list_models()
        return installed[0] if installed else "llama3.2:latest"

    def list_models(self) -> List[str]:
        """Queries local Ollama tags endpoint to return list of installed models."""
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if res.status_code == 200:
                data = res.json()
                models = [m["name"] for m in data.get("models", []) if "name" in m]
                return models
        except Exception:
            pass
        return ["llama3.2:latest", "deepseek-r1:latest", "qwen2.5:latest", "mistral:latest"]

    def is_connected(self) -> bool:
        """Checks if local Ollama daemon is reachable."""
        try:
            res = requests.get(f"{self.base_url}/api/version", timeout=2)
            return res.status_code == 200
        except Exception:
            return False

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Sends chat request to Ollama /api/chat endpoint."""
        target_model = self.model

        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        if response_format and response_format.get("type") == "json_object":
            payload["format"] = "json"

        try:
            res = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120
            )
            if res.status_code == 200:
                data = res.json()
                msg = data.get("message", {})
                content = msg.get("content", "")
                # Clean DeepSeek R1 / reasoning tags if present
                if "</think>" in content:
                    content = content.split("</think>")[-1].strip()
                return {
                    "content": content,
                    "model_used": target_model,
                    "provider": "ollama",
                    "raw": data
                }
            else:
                raise RuntimeError(f"Ollama returned HTTP {res.status_code}: {res.text[:200]}")
        except requests.ConnectionError:
            raise RuntimeError(f"Cannot reach local Ollama daemon at {self.base_url}. Ensure Ollama is running ('ollama serve').")
        except requests.Timeout:
            raise RuntimeError(f"Ollama generation timed out on model '{target_model}'. Try a smaller model or lower max_tokens.")
        except Exception as e:
            raise RuntimeError(f"Ollama error: {str(e)}")
