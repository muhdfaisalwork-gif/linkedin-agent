import os
from typing import Dict, Any, Optional
from .browser_agent import LinkedInBrowserAgent
from .publora_client import PubloraClient

class LinkedInDispatcher:
    """Dispatches publishing and profile update actions to the configured backend."""

    def __init__(self):
        self.browser_agent = LinkedInBrowserAgent()
        self.publora = PubloraClient()

    def get_active_backend(self) -> str:
        mode = os.getenv("LINKEDIN_EXECUTION_MODE")
        if not mode:
            try:
                from core.db.database import get_connection
                conn = get_connection()
                c = conn.cursor()
                c.execute("SELECT value FROM settings WHERE key = 'LINKEDIN_EXECUTION_MODE' LIMIT 1")
                row = c.fetchone()
                conn.close()
                if row and row[0]:
                    mode = row[0]
            except Exception:
                pass
        mode = (mode or "manual").lower()

        if mode == "browser" and self.browser_agent.is_authenticated():
            return "browser"
        elif mode == "publora" and self.publora.is_configured():
            return "publora"
        return "manual"

    def publish_post(self, content: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        backend = self.get_active_backend()

        if backend == "browser":
            # Map storage image url to local absolute file path
            local_image = None
            if image_url:
                if image_url.startswith("/storage/images/"):
                    img_name = image_url.split("/")[-1]
                    local_image = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage", "images", img_name)
                elif image_url.startswith("http://") or image_url.startswith("https://"):
                    try:
                        import requests
                        import uuid
                        img_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage", "images")
                        os.makedirs(img_dir, exist_ok=True)
                        tmp_path = os.path.join(img_dir, f"tmp_remote_{uuid.uuid4().hex[:8]}.jpg")
                        res = requests.get(image_url, timeout=20)
                        if res.status_code == 200:
                            with open(tmp_path, "wb") as f:
                                f.write(res.content)
                            local_image = tmp_path
                    except Exception:
                        pass
                elif os.path.exists(image_url):
                    local_image = image_url

            return self.browser_agent.publish_post(content, local_image)

        elif backend == "publora":
            media = [image_url] if image_url and image_url.startswith("http") else []
            return self.publora.create_post(content, media_urls=media)

        else:
            # Manual Mode
            return {
                "status": "manual",
                "message": "Post ready. Copy text to LinkedIn or connect your Browser session for 1-click auto-posting.",
                "clipboard_ready": True,
                "linkedin_composer_url": "https://www.linkedin.com/feed/?shareActive=true"
            }

    def update_profile(self, headline: Optional[str] = None, about: Optional[str] = None) -> Dict[str, Any]:
        backend = self.get_active_backend()
        if backend == "browser":
            return self.browser_agent.update_profile(headline=headline, about=about)
        else:
            return {
                "status": "manual",
                "message": "Profile copy generated. Navigate to LinkedIn to paste into your Headline/About, or connect Browser session.",
                "profile_url": "https://www.linkedin.com/in/me/edit/intro/"
            }

    def reply_to_comment(self, post_url: str, reply_text: str) -> Dict[str, Any]:
        backend = self.get_active_backend()
        if backend == "browser":
            return self.browser_agent.reply_to_comment(post_url=post_url, reply_text=reply_text)
        return {
            "status": "manual",
            "message": "Reply copied to clipboard. Paste into your LinkedIn post thread.",
            "post_url": post_url
        }

    def send_dm(self, recipient: str, message_text: str) -> Dict[str, Any]:
        backend = self.get_active_backend()
        if backend == "browser":
            return self.browser_agent.send_dm(recipient_profile_or_thread=recipient, message_text=message_text)
        return {
            "status": "manual",
            "message": "Direct message drafted and copied to clipboard.",
            "recipient": recipient
        }
