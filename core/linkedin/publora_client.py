import os
from typing import Dict, Any, Optional
import requests

class PubloraClient:
    BASE_URL = "https://api.publora.com/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        self._explicit_api_key = api_key

    @property
    def api_key(self) -> Optional[str]:
        if self._explicit_api_key:
            return self._explicit_api_key
        try:
            from core.llm.client import _get_db_setting
            return os.getenv("PUBLORA_API_KEY") or _get_db_setting("PUBLORA_API_KEY")
        except Exception:
            return os.getenv("PUBLORA_API_KEY")

    @property
    def platform_id(self) -> Optional[str]:
        try:
            from core.llm.client import _get_db_setting
            return os.getenv("LINKEDIN_PLATFORM_ID") or _get_db_setting("LINKEDIN_PLATFORM_ID")
        except Exception:
            return os.getenv("LINKEDIN_PLATFORM_ID")

    def is_configured(self) -> bool:
        return bool(self.api_key and self.platform_id)

    def create_post(self, content: str, media_urls: Optional[list] = None) -> Dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError("PUBLORA_API_KEY or LINKEDIN_PLATFORM_ID not set.")

        platform_id = self.platform_id
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
            if res.status_code in (200, 201):
                try:
                    data = res.json()
                    if isinstance(data, dict):
                        if "status" not in data:
                            data["status"] = "success" if data.get("success", True) else "error"
                        return data
                    return {"status": "success", "data": data}
                except Exception:
                    return {"status": "success", "message": res.text}
            else:
                return {"status": "error", "message": f"Publora HTTP {res.status_code}: {res.text[:200]}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_comment(self, post_urn: str, message: str, parent_comment: Optional[str] = None) -> Dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError("PUBLORA_API_KEY not set.")

        platform_id = self.platform_id
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
            if res.status_code in (200, 201):
                try:
                    data = res.json()
                    if isinstance(data, dict):
                        if "status" not in data:
                            data["status"] = "success" if data.get("success", True) else "error"
                        return data
                    return {"status": "success", "data": data}
                except Exception:
                    return {"status": "success", "message": res.text}
            else:
                return {"status": "error", "message": f"Publora HTTP {res.status_code}: {res.text[:200]}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
