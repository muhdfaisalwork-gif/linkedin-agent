import os
import base64
import json
from typing import Dict, Any, Optional
from core.llm.client import OpenRouterClient

class ReachVisionAnalyzer:
    """
    Multimodal Vision Engine ("Eyes for the Agent"):
    Analyzes page screenshots, evaluates post graphics, extracts visual hooks,
    and detects UI elements using multimodal vision models.
    """

    def __init__(self, llm_client: Optional[OpenRouterClient] = None):
        self.llm = llm_client or OpenRouterClient()

    def _encode_image_to_base64(self, image_path: str) -> Optional[str]:
        if not os.path.exists(image_path):
            return None
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return None

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

        # Check if vision model is specified or use default vision model
        # Models with vision support: google/gemini-2.0-flash-exp:free, google/gemini-flash-1.5, openai/gpt-4o, anthropic/claude-3.5-sonnet
        vision_model = os.getenv("VISION_MODEL")
        if not vision_model:
            cur_model = os.getenv("OPENROUTER_MODEL", "")
            if any(k in cur_model for k in ["gemini", "gpt-4", "claude", "vision", "qwen-vl"]):
                vision_model = cur_model
            else:
                vision_model = "google/gemini-2.0-flash-exp:free"

        prompt = context_prompt or (
            "You are the visual cortex of an autonomous LinkedIn agent. Look at this LinkedIn screen/post screenshot and analyze:\n"
            "1. Visual Hierarchy: What grabs the eye first? Hook, image, headline, or numbers?\n"
            "2. Readability & Spacing: Does the post format follow clean mobile line breaks or is it a wall of text?\n"
            "3. Interactive Elements: Locate the visible Like, Comment, and Repost buttons and reaction counts.\n"
            "4. Strategic Takeaway: What is the primary takeaway or conversational opening for a human reply?\n"
            "Keep the feedback crisp, candid, and builder-focused."
        )

        try:
            import urllib.request
            api_key = self.llm.api_key
            if not api_key:
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

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://linkedin-nexus-agent.local",
                "X-Title": "LinkedIn Nexus Agent Vision Cortex"
            }

            payload = {
                "model": vision_model,
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

            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                result_text = data["choices"][0]["message"]["content"]
                return {
                    "status": "success",
                    "vision_model": vision_model,
                    "analysis": result_text
                }
        except Exception as e:
            # Fallback heuristic summary if network or vision model fails
            return {
                "status": "fallback",
                "vision_model": "cortex-fallback",
                "analysis": f"Visual scan completed. Screenshot preserved at {os.path.basename(image_path)}. (Vision API note: {str(e)[:120]})"
            }
