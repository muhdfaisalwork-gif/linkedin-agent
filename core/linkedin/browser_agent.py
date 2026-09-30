import os
import json
import time
import concurrent.futures
from typing import Dict, Any, Optional, List

USER_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage", "browser_state")
os.makedirs(USER_DATA_DIR, exist_ok=True)

class LinkedInBrowserAgent:
    """
    Open-source Playwright browser engine for direct, unrestricted LinkedIn automation:
    - Post creation with attached image
    - Profile headline & About updates
    - Comment thread sweeps & replies
    - Inbox direct message management
    """

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.user_data_dir = USER_DATA_DIR

    def is_playwright_available(self) -> bool:
        try:
            import playwright
            return True
        except ImportError:
            return False

    def is_authenticated(self) -> bool:
        """Checks if saved session cookies exist in user data directory."""
        net_cookies = os.path.join(self.user_data_dir, "Default", "Network", "Cookies")
        root_cookies = os.path.join(self.user_data_dir, "Default", "Cookies")
        for path in [net_cookies, root_cookies]:
            if os.path.exists(path) and os.path.getsize(path) > 1024:
                return True
        return False

    def _run_in_worker_thread(self, fn, *args, timeout: int = 60, **kwargs) -> Any:
        """Runs synchronous Playwright operations in an isolated worker thread to avoid asyncio event loop conflicts."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(fn, *args, **kwargs)
            try:
                return future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                return {"status": "error", "message": f"Browser operation timed out after {timeout} seconds."}

    def _launch_context(self, playwright_instance, headless: bool = False, viewport: Optional[Dict[str, int]] = None):
        """
        Launches persistent context with intelligent channel fallback:
        Tries system Google Chrome -> Microsoft Edge -> standalone Playwright Chromium.
        """
        channels = ["chrome", "msedge", None]
        errors = []
        for ch in channels:
            try:
                kwargs = {
                    "user_data_dir": self.user_data_dir,
                    "headless": headless,
                    "args": ["--disable-blink-features=AutomationControlled"]
                }
                if ch:
                    kwargs["channel"] = ch
                if viewport:
                    kwargs["viewport"] = viewport
                return playwright_instance.chromium.launch_persistent_context(**kwargs)
            except Exception as e:
                errors.append(f"{ch or 'default'}: {str(e)}")
                continue

        raise RuntimeError(f"Could not launch browser context. Attempted channels: {errors}")

    def launch_interactive_login(self) -> Dict[str, Any]:
        """Opens a headed browser window so the user can log in to LinkedIn once safely."""
        if not self.is_playwright_available():
            return {
                "status": "error",
                "message": "Playwright is not installed. Run 'pip install playwright && playwright install chromium' to enable browser automation."
            }

        def _action():
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                context = self._launch_context(p, headless=False, viewport={"width": 1280, "height": 850})
                page = context.pages[0] if context.pages else context.new_page()
                page.goto("https://www.linkedin.com/login")

                # Poll up to 180 seconds for user to complete login
                # Detects if user reaches feed, profile, or closes the window
                logged_in = False
                for _ in range(180):
                    try:
                        time.sleep(1)
                        if page.is_closed():
                            break
                        cur_url = page.url.lower()
                        # If reached feed or profile page, login was successful
                        if any(k in cur_url for k in ["/feed", "/in/", "/mynetwork", "/messaging"]):
                            logged_in = True
                            # Wait 2 seconds for session cookies to be written to storage
                            time.sleep(2)
                            break
                    except Exception:
                        break

                try:
                    context.close()
                except Exception:
                    pass

                if logged_in or self.is_authenticated():
                    return {"status": "success", "message": "LinkedIn connected successfully! Your session is saved."}
                else:
                    return {"status": "cancelled", "message": "Browser was closed before LinkedIn login finished. Please try again."}

        try:
            return self._run_in_worker_thread(_action, timeout=190)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def publish_post(self, content: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        """Publishes post with image via headless browser."""
        if not self.is_playwright_available():
            return {"status": "error", "message": "Playwright not installed."}

        def _action():
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                context = self._launch_context(p, headless=self.headless)
                page = context.pages[0] if context.pages else context.new_page()
                page.goto("https://www.linkedin.com/feed/")
                page.wait_for_load_state("domcontentloaded")

                # Check if logged in
                if "login" in page.url or "checkpoint" in page.url:
                    context.close()
                    return {"status": "auth_required", "message": "Please connect your LinkedIn session in Settings."}

                # Click 'Start a post'
                start_btn = page.locator("button:has-text('Start a post'), button.share-box-feed-entry__trigger, div[aria-label*='Start a post' i]").first
                if start_btn.count() > 0:
                    start_btn.click()
                else:
                    page.click("button:has-text('Start a post')")
                page.wait_for_timeout(1200)

                # Attach image if provided
                if image_path and os.path.exists(image_path):
                    # Check if file input is in DOM or click media button first
                    file_input = page.locator("input[type='file']").first
                    if file_input.count() == 0:
                        media_btn = page.locator("button[aria-label*='photo' i], button[aria-label*='media' i], button[aria-label*='Add media' i]").first
                        if media_btn.count() > 0:
                            media_btn.click()
                            page.wait_for_timeout(1000)
                            file_input = page.locator("input[type='file']").first

                    if file_input.count() > 0:
                        file_input.set_input_files(image_path)
                        page.wait_for_timeout(2000)
                        done_btn = page.locator("button:has-text('Next'), button:has-text('Done'), button.share-box-footer__primary-btn").first
                        if done_btn.count() > 0:
                            done_btn.click()
                            page.wait_for_timeout(1000)

                # Type content into post composer
                editor = page.locator("div.ql-editor, div[role='textbox'], div[contenteditable='true']").first
                if editor.count() > 0:
                    editor.click()
                    editor.fill(content)
                page.wait_for_timeout(1000)

                # Click Post button
                post_btn = page.locator("button:has-text('Post'), button.share-actions__primary-action").first
                if post_btn.count() > 0:
                    post_btn.click()
                page.wait_for_timeout(3000)

                context.close()
                return {"status": "success", "message": "Post published to LinkedIn via Browser Agent."}

        try:
            return self._run_in_worker_thread(_action)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def update_profile(self, headline: Optional[str] = None, about: Optional[str] = None) -> Dict[str, Any]:
        """Navigates to LinkedIn profile and updates Headline / About."""
        if not self.is_playwright_available():
            return {"status": "error", "message": "Playwright not installed."}

        def _action():
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                context = self._launch_context(p, headless=self.headless)
                page = context.pages[0] if context.pages else context.new_page()
                page.goto("https://www.linkedin.com/in/me/")
                page.wait_for_load_state("domcontentloaded")

                # Check if logged in
                if "login" in page.url or "checkpoint" in page.url:
                    context.close()
                    return {"status": "auth_required", "message": "Please connect your LinkedIn session in Settings."}

                if headline:
                    edit_intro = page.locator("button[aria-label='Edit intro']").first
                    if edit_intro.count() > 0:
                        edit_intro.click()
                        page.wait_for_timeout(1200)
                        headline_input = page.locator("input[name='headline'], input[id*='headline' i], input#single-line-text-form-component-profileEditFormElement-TOP-CARD-headline").first
                        if headline_input.count() > 0:
                            headline_input.fill(headline)
                        save_btn = page.locator("button:has-text('Save')").first
                        if save_btn.count() > 0:
                            save_btn.click()
                            page.wait_for_timeout(2000)

                if about:
                    page.goto("https://www.linkedin.com/in/me/")
                    page.wait_for_load_state("domcontentloaded")
                    edit_about = page.locator("button[aria-label='Edit about'], a[href*='/edit/about']").first
                    if edit_about.count() > 0:
                        edit_about.click()
                        page.wait_for_timeout(1200)
                        about_input = page.locator("textarea[name='summary'], textarea[id*='summary' i], div[role='dialog'] textarea").first
                        if about_input.count() > 0:
                            about_input.fill(about)
                            save_btn = page.locator("button:has-text('Save')").first
                            if save_btn.count() > 0:
                                save_btn.click()
                                page.wait_for_timeout(2000)

                context.close()
                return {"status": "success", "message": "Profile updated successfully via Browser Agent."}

        try:
            return self._run_in_worker_thread(_action)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def reply_to_comment(self, post_url: str, reply_text: str) -> Dict[str, Any]:
        """Navigates to a LinkedIn post and publishes a comment or reply."""
        if not self.is_playwright_available():
            return {"status": "error", "message": "Playwright not installed."}

        def _action():
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                context = self._launch_context(p, headless=self.headless)
                page = context.pages[0] if context.pages else context.new_page()
                page.goto(post_url)
                page.wait_for_load_state("domcontentloaded")

                if "login" in page.url or "checkpoint" in page.url:
                    context.close()
                    return {"status": "auth_required", "message": "Please connect your LinkedIn session in Settings."}

                comment_box = page.locator("div.comments-comment-box div[role='textbox'], div[role='textbox'][aria-label*='comment' i], div.ql-editor").first
                if comment_box.count() > 0:
                    comment_box.click()
                    comment_box.fill(reply_text)
                    page.wait_for_timeout(1000)
                    submit_btn = page.locator("button:has-text('Comment'), button.comments-comment-box__submit-button").first
                    if submit_btn.count() > 0:
                        submit_btn.click()
                        page.wait_for_timeout(2000)
                        context.close()
                        return {"status": "success", "message": "Comment reply published to LinkedIn via Browser Agent."}

                context.close()
                return {"status": "error", "message": "Could not locate comment input on target post."}

        try:
            return self._run_in_worker_thread(_action)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def send_dm(self, recipient_profile_or_thread: str, message_text: str) -> Dict[str, Any]:
        """Sends a direct message to a user or thread via browser automation."""
        if not self.is_playwright_available():
            return {"status": "error", "message": "Playwright not installed."}

        def _action():
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                context = self._launch_context(p, headless=self.headless)
                page = context.pages[0] if context.pages else context.new_page()

                # If recipient is a full URL or profile name
                url = recipient_profile_or_thread if recipient_profile_or_thread.startswith("http") else f"https://www.linkedin.com/in/{recipient_profile_or_thread.strip('/')}/"
                page.goto(url)
                page.wait_for_load_state("domcontentloaded")

                if "login" in page.url or "checkpoint" in page.url:
                    context.close()
                    return {"status": "auth_required", "message": "Please connect your LinkedIn session in Settings."}

                # Click Message button on profile
                msg_btn = page.locator("button:has-text('Message'), a[href*='/messaging/thread/']").first
                if msg_btn.count() > 0:
                    msg_btn.click()
                    page.wait_for_timeout(1500)

                # Type into messaging composer
                chat_box = page.locator("div.msg-form__contenteditable[role='textbox'], div[role='textbox'][aria-label*='message' i]").first
                if chat_box.count() > 0:
                    chat_box.click()
                    chat_box.fill(message_text)
                    page.wait_for_timeout(1000)

                    send_btn = page.locator("button[type='submit']:has-text('Send'), button.msg-form__send-button").first
                    if send_btn.count() > 0:
                        send_btn.click()
                        page.wait_for_timeout(2000)
                        context.close()
                        return {"status": "success", "message": "Direct message sent via Browser Agent."}

                context.close()
                return {"status": "error", "message": "Could not locate chat input or recipient message button."}

        try:
            return self._run_in_worker_thread(_action)
        except Exception as e:
            return {"status": "error", "message": str(e)}
