import os
import urllib.parse
import uuid
import requests
from typing import Dict, Any, Optional
from .quote_card import QuoteCardRenderer, STORAGE_DIR

class ImageGenerator:
    """Generates visual assets (AI Art or Typeset Quote-Cards) for LinkedIn posts."""

    @staticmethod
    def generate_ai_image(prompt: str, aspect_ratio: str = "1:1") -> str:
        """
        Generates high-definition AI art via Pollinations.ai (Flux engine).
        Completely free, fast, no API key required.
        """
        width, height = (1080, 1080)
        if aspect_ratio == "4:5":
            width, height = (1080, 1350)
        elif aspect_ratio == "16:9":
            width, height = (1280, 720)

        # Clean prompt for URL encoding
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model=flux&nologo=true&enhance=true"

        filename = f"flux_{uuid.uuid4().hex[:10]}.jpg"
        filepath = os.path.join(STORAGE_DIR, filename)

        try:
            res = requests.get(url, timeout=12)
            if res.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(res.content)
                return f"/storage/images/{filename}"
        except Exception:
            pass

        # Fallback to direct URL if local download failed
        return url

    @staticmethod
    def generate_quote_card(quote: str, author: str = "Founder & Architect", handle: str = "@raulfinternational") -> str:
        """Generates a typeset quote card locally."""
        return QuoteCardRenderer.render_quote_card(quote, author_name=author, handle=handle)

    @classmethod
    def create_post_visual(
        cls,
        hook: str,
        topic: str,
        visual_type: str = "ai_image",
        author_name: str = "Founder & Architect"
    ) -> Dict[str, str]:
        """Creates either an AI art illustration or a quote card based on post content."""
        if visual_type == "quote_card":
            url = cls.generate_quote_card(hook, author=author_name)
            return {"type": "quote_card", "url": url}
        else:
            prompt = f"Professional conceptual 3D render representing {topic}, clean modern lighting, high tech minimal aesthetic, no text"
            url = cls.generate_ai_image(prompt)
            return {"type": "ai_image", "url": url, "prompt": prompt}
