import time
import threading
from datetime import datetime
from typing import Optional
from core.db.database import get_connection
from core.linkedin.dispatcher import LinkedInDispatcher
from core.brain.reflector import Reflector
from core.llm.client import OpenRouterClient

class AutonomousAgentRunner:
    """Background autonomous worker that checks scheduled posts and runs periodic cycles."""

    def __init__(self, check_interval_seconds: int = 60):
        self.interval = check_interval_seconds
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.dispatcher = LinkedInDispatcher()

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.is_running = False
        self._stop_event.set()

    def _run_loop(self):
        while self.is_running and not self._stop_event.is_set():
            try:
                self.check_scheduled_posts()
            except Exception:
                pass
            if self._stop_event.wait(self.interval):
                break

    def check_scheduled_posts(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM posts
            WHERE status = 'scheduled' AND datetime(replace(scheduled_time, 'T', ' ')) <= datetime('now')
        ''')
        due_posts = cursor.fetchall()

        for post in due_posts:
            try:
                # Dispatch publish
                result = self.dispatcher.publish_post(post["content"], post["image_url"])
                if result.get("status") != "error":
                    cursor.execute('''
                        UPDATE posts
                        SET status = 'published', published_time = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (post["id"],))
                else:
                    cursor.execute('''
                        UPDATE posts
                        SET status = 'failed'
                        WHERE id = ?
                    ''', (post["id"],))
                conn.commit()
            except Exception:
                pass

        conn.close()
