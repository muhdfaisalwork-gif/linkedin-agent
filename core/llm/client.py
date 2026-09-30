import os
import time
import random
import json
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

class OpenRouterClient:
    BASE_URL = "https://openrouter.ai/api/v1"

    DEFAULT_FALLBACKS = [
        "inclusionai/ling-3.0-flash-sante:free",
        "liquid/lfm-2.5-2.6b:free",
        "dots-studio/dots-3-note-preview:free",
        "stealth/space-bunny-alpha",
        "google/gemma-4-31b-it:free",
        "google/gemma-4-26b-a4b-it:free"
    ]

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self._explicit_api_key = api_key
        self._explicit_model = model

        env_fallbacks = os.getenv("FALLBACK_MODELS")
        if env_fallbacks:
            self.fallback_models = [m.strip() for m in env_fallbacks.split(",") if m.strip()]
        else:
            self.fallback_models = self.DEFAULT_FALLBACKS.copy()

    @property
    def api_key(self) -> Optional[str]:
        return self._explicit_api_key or os.getenv("OPENROUTER_API_KEY")

    @property
    def current_model(self) -> str:
        return self._explicit_model or os.getenv("OPENROUTER_MODEL", "inclusionai/ling-3.0-flash-sante:free")

    @property
    def active_chain(self) -> List[str]:
        cur = self.current_model
        chain = [cur]
        for m in self.fallback_models:
            if m != cur and m not in chain:
                chain.append(m)
        return chain

    def _headers(self) -> Dict[str, str]:
        key = self.api_key or ""
        return {
            "Authorization": f"Bearer {key}",
            "HTTP-Referer": "https://github.com/nexus-linkedin-agent",
            "X-Title": "NexusAgent LinkedIn Studio",
            "Content-Type": "application/json"
        }

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Execute chat completion with automatic model fallback and retry."""
        if not self.api_key:
            raise ValueError("OpenRouter API Key is missing. Please enter your key in the Settings tab or set OPENROUTER_API_KEY.")

        last_error = None

        for model_candidate in self.active_chain:
            payload: Dict[str, Any] = {
                "model": model_candidate,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            if response_format:
                payload["response_format"] = response_format

            for attempt in range(2):
                try:
                    res = requests.post(
                        f"{self.BASE_URL}/chat/completions",
                        headers=self._headers(),
                        json=payload,
                        timeout=40
                    )

                    if res.status_code == 200:
                        data = res.json()
                        choices = data.get("choices")
                        choice = choices[0] if (choices and isinstance(choices, list)) else {}
                        msg = choice.get("message", {}) if isinstance(choice, dict) else {}
                        content = msg.get("content") or (choice.get("text") if isinstance(choice, dict) else "") or (msg.get("reasoning") if isinstance(msg, dict) else "") or ""
                        if not content and choices and len(choices) > 0:
                            # If content is empty or null, try next model candidate
                            last_error = f"Model {model_candidate} returned empty content: {data}"
                            break

                        return {
                            "content": str(content),
                            "model_used": model_candidate,
                            "raw": data
                        }

                    elif res.status_code in (429, 502, 503, 504):
                        # Rate limit or temporary error - backoff slightly
                        wait = (1.5 ** attempt) + random.uniform(0.5, 1.5)
                        time.sleep(wait)
                        last_error = f"Model {model_candidate} returned {res.status_code}: {res.text[:150]}"
                        continue
                    else:
                        last_error = f"Model {model_candidate} returned HTTP {res.status_code}: {res.text[:150]}"
                        break  # Non-retryable on this model, try next model

                except requests.RequestException as e:
                    last_error = f"Request error for {model_candidate}: {str(e)}"
                    time.sleep(1.0)
                    continue

        raise RuntimeError(f"All OpenRouter models in fallback chain failed. Last error: {last_error}")

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        res = self.chat_completion(messages, temperature=temperature)
        return res["content"].strip()

    def get_available_free_models(self) -> List[str]:
        try:
            res = requests.get(f"{self.BASE_URL}/models", headers=self._headers(), timeout=15)
            if res.status_code == 200:
                models = res.json().get("data", [])
                free = [
                    m["id"] for m in models
                    if ":free" in m["id"] or (
                        m.get("pricing", {}).get("prompt") == "0" and m.get("pricing", {}).get("completion") == "0"
                    )
                ]
                return free
        except Exception:
            pass
        return self.DEFAULT_FALLBACKS
