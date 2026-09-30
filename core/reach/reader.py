import os
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional
from core.linkedin.browser_agent import LinkedInBrowserAgent

class ReachReader:
    """
    Dual-backend internet and LinkedIn page reader inspired by Agent-Reach:
    - Backend 1 (High-speed Jina Reader): Converts web pages and public profiles into clean Markdown.
    - Backend 2 (Headless Browser DOM): Fallback for authenticated feeds, internal LinkedIn updates, and dynamic JS content.
    """

    def __init__(self, browser_agent: Optional[LinkedInBrowserAgent] = None):
        self.browser_agent = browser_agent or LinkedInBrowserAgent(headless=True)
        self.jina_prefix = "https://r.jina.ai/"

    def read_url(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """
        Reads any URL using smart backend routing:
        Tries Jina Reader first for fast, lightweight Markdown extraction.
        Falls back to Playwright headless browser for JavaScript-heavy or login-protected pages.
        """
        url = url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"

        # 1. Try Jina Reader
        try:
            jina_url = f"{self.jina_prefix}{url}"
            req = urllib.request.Request(
                jina_url,
                headers={
                    "User-Agent": "LinkedInNexusAgent/1.0",
                    "Accept": "text/markdown, text/plain"
                }
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                content = resp.read().decode("utf-8", errors="ignore")
                if content and len(content.strip()) > 80 and "Captcha" not in content and "Access Denied" not in content:
                    lines = [line.strip() for line in content.split("\n") if line.strip()]
                    title = lines[0].replace("#", "").strip() if lines else "Extracted Article"
                    return {
                        "status": "success",
                        "backend": "jina_reader",
                        "url": url,
                        "title": title[:120],
                        "content": content[:6000],
                        "summary": content[:400] + "..." if len(content) > 400 else content
                    }
        except Exception:
            pass

        # 2. Fallback to Browser Agent (Headless DOM)
        if self.browser_agent.is_playwright_available():
            try:
                def _browser_read():
                    from playwright.sync_api import sync_playwright
                    with sync_playwright() as p:
                        context = self.browser_agent._launch_context(p, headless=True)
                        page = context.pages[0] if context.pages else context.new_page()
                        page.goto(url, wait_until="domcontentloaded", timeout=25000)
                        page.wait_for_timeout(2000)
                        
                        title = page.title()
                        text = page.evaluate("() => document.body.innerText")
                        context.close()
                        return {
                            "title": title,
                            "text": text
                        }

                res = self.browser_agent._run_in_worker_thread(_browser_read, timeout=30)
                if isinstance(res, dict) and "text" in res:
                    clean_text = "\n".join([line.strip() for line in res["text"].split("\n") if line.strip()])
                    return {
                        "status": "success",
                        "backend": "playwright_browser",
                        "url": url,
                        "title": res.get("title", "LinkedIn Page")[:120],
                        "content": clean_text[:6000],
                        "summary": clean_text[:400] + "..." if len(clean_text) > 400 else clean_text
                    }
            except Exception as e:
                return {
                    "status": "error",
                    "url": url,
                    "message": f"Both Jina Reader and Playwright failed to read URL: {str(e)}"
                }

        return {
            "status": "error",
            "url": url,
            "message": "Unable to extract content from the provided URL."
        }
