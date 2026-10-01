from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers (Ollama, OpenAI, Claude, Gemini, OpenRouter)."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g. 'ollama', 'openai', 'anthropic', 'gemini', 'openrouter')."""
        pass

    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Executes chat completion.
        Returns dict with:
        {
            "content": str,
            "model_used": str,
            "provider": str,
            "raw": dict (optional)
        }
        """
        pass

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Convenience method to generate text from a prompt."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        res = self.chat_completion(messages, temperature=temperature)
        return res["content"].strip()

    @abstractmethod
    def list_models(self) -> List[str]:
        """Returns list of available models for this provider."""
        pass
