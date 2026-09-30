import os
from typing import Dict, Any, Optional
import requests

class PubloraClient:
    BASE_URL = "https://api.publora.com/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        self._explicit_api_key = api_key

    @property
    def api_key(self) -> Optional[str]:
        return self._explicit_api_key or os.getenv("PUBLORA_API_KEY")

    def is_configured(self) -> bool:
        return bool(self.api_key and os.getenv("LINKEDIN_PLATFORM_ID"))

    def create_post(self, content: str, media_urls: Optional[list] = None) -> Dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError("PUBLORA_API_KEY or LINKEDIN_PLATFORM_ID not set.")

        platform_id = os.getenv("LINKEDIN_PLATFORM_ID")
        headers = {
            "x-publora-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "content": content,
            "platforms": [platform_id],
            "mediaUrls": media_urls or []
        }

        try:
            res = requests.post(f"{self.BASE_URL}/create-post", headers=headers, json=payload, timeout=30)
            return res.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_comment(self, post_urn: str, message: str, parent_comment: Optional[str] = None) -> Dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError("PUBLORA_API_KEY not set.")

        platform_id = os.getenv("LINKEDIN_PLATFORM_ID")
        headers = {
            "x-publora-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "postedId": post_urn,
            "message": message,
            "platformId": platform_id,
            "parentComment": parent_comment
        }

        try:
            res = requests.post(f"{self.BASE_URL}/linkedin-comments", headers=headers, json=payload, timeout=30)
            return res.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
