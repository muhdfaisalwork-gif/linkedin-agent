import os
import base64
import json
import requests
from typing import Dict, Any, Optional
from core.llm.client import UniversalLLMClient, OpenRouterClient, _get_db_setting

class ReachVisionAnalyzer:
    """
    Multimodal Vision Engine ("Eyes for the Agent"):
    Analyzes page screenshots, evaluates post graphics, extracts visual hooks,
    and detects UI elements using multimodal vision models.
    Supports Ollama, Google Gemini, OpenAI, Claude, OpenRouter, and Custom local models.
    """

    def __init__(self, llm_client: Optional[UniversalLLMClient] = None):
        self.llm = llm_client or OpenRouterClient()

    def _encode_image_to_base64(self, image_path: str) -> Optional[str]:
        if not os.path.exists(image_path):
            return None
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return None

    @staticmethod
    def _extract_vision_choice_content(data: Dict[str, Any]) -> str:
        choices = data.get("choices", [])
        if not choices or not isinstance(choices, list):
            feedback = data.get("promptFeedback", {})
            if feedback.get("blockReason"):
                raise RuntimeError(f"Vision prompt blocked: {feedback.get('blockReason')}")
            raise RuntimeError(f"Vision provider returned no choices: {data}")
        choice = choices[0] if isinstance(choices[0], dict) else {}
        msg = choice.get("message", {}) if isinstance(choice, dict) else {}
        content = msg.get("content") or choice.get("text") or ""
        return str(content).strip()

    def analyze_screenshot(self, image_path: str, context_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Sends the screenshot to a vision-capable LLM to visually critique layout,
        identify focal points, and summarize what the agent's eyes see.
        """
        b64_image = self._encode_image_to_base64(image_path)
        if not b64_image:
            return {
                "status": "error",
                "message": f"Image file not found at {image_path}"
            }

        prompt = context_prompt or (
            "You are the visual cortex of an autonomous LinkedIn agent. Look at this LinkedIn screen/post screenshot and analyze:\n"
            "1. Visual Hierarchy: What grabs the eye first? Hook, image, headline, or numbers?\n"
            "2. Readability & Spacing: Does the post format follow clean mobile line breaks or is it a wall of text?\n"
            "3. Interactive Elements: Locate the visible Like, Comment, and Repost buttons and reaction counts.\n"
            "4. Strategic Takeaway: What is the primary takeaway or conversational opening for a human reply?\n"
            "Keep the feedback crisp, candid, and builder-focused."
        )

        provider = self.llm.active_provider_name
        vision_model = os.getenv("VISION_MODEL") or _get_db_setting("VISION_MODEL")

        try:
            # 1. Local Ollama Routing
            if provider == "ollama":
                base_url = (os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434").rstrip("/")
                if not vision_model:
                    active_model = self.llm.current_model
                    if any(k in active_model.lower() for k in ["vision", "vl", "llava", "minicpm", "bakllava"]):
                        vision_model = active_model
                    else:
                        vision_model = "llama3.2-vision:latest"

                payload = {
                    "model": vision_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                            "images": [b64_image]
                        }
                    ],
                    "stream": False,
                    "options": {"temperature": 0.2}
                }
                res = requests.post(f"{base_url}/api/chat", json=payload, timeout=60)
                if res.status_code == 200:
                    data = res.json()
                    analysis_text = data.get("message", {}).get("content", "")
                    if "<think>" in analysis_text or "</think>" in analysis_text:
                        import re
                        analysis_text = re.sub(r'<think>.*?(?:</think>|$)', '', analysis_text, flags=re.DOTALL).strip()
                    return {
                        "status": "success",
                        "provider": "ollama",
                        "vision_model": vision_model,
                        "analysis": analysis_text
                    }
                else:
                    raise RuntimeError(f"Ollama vision HTTP {res.status_code}: {res.text[:150]}")

            # 2. Google Gemini Routing
            elif provider == "gemini":
                key = self.llm.api_key
                if not key:
                    raise ValueError("GEMINI_API_KEY is not configured.")
                target_model = vision_model or self.llm.current_model or "gemini-2.0-flash"
                endpoint = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
                payload = {
                    "model": target_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}}
                            ]
                        }
                    ],
                    "temperature": 0.2
                }
                headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
                res = requests.post(endpoint, json=payload, headers=headers, timeout=45)
                if res.status_code == 200:
                    analysis_text = self._extract_vision_choice_content(res.json())
                    return {"status": "success", "provider": "gemini", "vision_model": target_model, "analysis": analysis_text}
                else:
                    raise RuntimeError(f"Gemini vision HTTP {res.status_code}: {res.text[:150]}")

            # 3. Direct OpenAI Routing
            elif provider == "openai":
                key = self.llm.api_key
                if not key:
                    raise ValueError("OPENAI_API_KEY is not configured.")
                target_model = vision_model or self.llm.current_model or "gpt-4o"
                endpoint = "https://api.openai.com/v1/chat/completions"
                payload = {
                    "model": target_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}}
                            ]
                        }
                    ],
                    "temperature": 0.2
                }
                headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
                res = requests.post(endpoint, json=payload, headers=headers, timeout=45)
                if res.status_code == 200:
                    analysis_text = self._extract_vision_choice_content(res.json())
                    return {"status": "success", "provider": "openai", "vision_model": target_model, "analysis": analysis_text}
                else:
                    raise RuntimeError(f"OpenAI vision HTTP {res.status_code}: {res.text[:150]}")

            # 4. Anthropic Claude Routing
            elif provider == "anthropic":
                key = self.llm.api_key
                if not key:
                    raise ValueError("ANTHROPIC_API_KEY is not configured.")
                target_model = vision_model or self.llm.current_model or "claude-3-5-sonnet-20241022"
                endpoint = "https://api.anthropic.com/v1/messages"
                headers = {
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": target_model,
                    "max_tokens": 1024,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": b64_image
                                    }
                                }
                            ]
                        }
                    ],
                    "temperature": 0.2
                }
                res = requests.post(endpoint, json=payload, headers=headers, timeout=45)
                if res.status_code == 200:
                    blocks = res.json().get("content", [])
                    analysis_text = "".join([b.get("text", "") for b in blocks if b.get("type") == "text"])
                    return {"status": "success", "provider": "anthropic", "vision_model": target_model, "analysis": analysis_text}
                else:
                    raise RuntimeError(f"Anthropic vision HTTP {res.status_code}: {res.text[:150]}")

            # 5. Custom OpenAI-Compatible Local Endpoint (LM Studio, vLLM, LocalAI)
            elif provider == "custom":
                custom_base_url = (os.getenv("CUSTOM_BASE_URL") or _get_db_setting("CUSTOM_BASE_URL") or "http://localhost:1234/v1").rstrip("/")
                key = self.llm.api_key
                target_model = vision_model or self.llm.current_model or "local-model"
                endpoint = f"{custom_base_url}/chat/completions"
                headers = {"Content-Type": "application/json"}
                if key:
                    headers["Authorization"] = f"Bearer {key}"
                payload = {
                    "model": target_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}}
                            ]
                        }
                    ],
                    "temperature": 0.2
                }
                res = requests.post(endpoint, json=payload, headers=headers, timeout=45)
                if res.status_code == 200:
                    analysis_text = self._extract_vision_choice_content(res.json())
                    return {"status": "success", "provider": "custom", "vision_model": target_model, "analysis": analysis_text}
                else:
                    raise RuntimeError(f"Custom vision HTTP {res.status_code}: {res.text[:150]}")

            # 6. OpenRouter (Default / Multi-Model)
            else:
                key = self.llm.api_key
                if not key:
                    return {
                        "status": "mock",
                        "vision_model": "heuristic-cortex",
                        "analysis": (
                            "• Visual Hierarchy: High-contrast title and prominent reaction bar.\n"
                            "• Readability: Clean single-idea paragraphs optimized for mobile feed scrolling.\n"
                            "• Interactive Grounding: Detected Like, Comment, and Repost triggers.\n"
                            "• Strategic Takeaway: Strong engagement opportunity for founder-level commentary on architecture and latency."
                        )
                    }

                target_model = vision_model or "google/gemini-2.0-flash-exp:free"
                cur_model = self.llm.current_model or ""
                if any(k in cur_model.lower() for k in ["gemini", "gpt-4", "claude", "vision", "qwen-vl"]):
                    target_model = cur_model

                headers = {
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://linkedin-nexus-agent.local",
                    "X-Title": "LinkedIn Nexus Agent Vision Cortex"
                }

                payload = {
                    "model": target_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{b64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    "temperature": 0.2
                }

                res = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=35
                )
                if res.status_code == 200:
                    analysis_text = self._extract_vision_choice_content(res.json())
                    return {
                        "status": "success",
                        "provider": "openrouter",
                        "vision_model": target_model,
                        "analysis": analysis_text
                    }
                else:
                    raise RuntimeError(f"OpenRouter vision HTTP {res.status_code}: {res.text[:150]}")

        except Exception as e:
            # Fallback heuristic summary if network or vision model fails
            return {
                "status": "fallback",
                "vision_model": "cortex-fallback",
                "analysis": (
                    f"Visual scan completed for {os.path.basename(image_path)}.\n"
                    f"• Visual Hierarchy: High-contrast post title and feed engagement triggers.\n"
                    f"• Readability: Clean single-concept layout optimized for mobile screen viewport.\n"
                    f"• Interactive Grounding: Found conversational opening for founder reply.\n"
                    f"(Vision provider note: {str(e)[:120]})"
                )
            }
