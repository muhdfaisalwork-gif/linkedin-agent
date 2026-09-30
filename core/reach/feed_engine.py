import os
import json
import sqlite3
from typing import Dict, Any, List, Optional
from core.db.database import get_connection
from core.linkedin.browser_agent import LinkedInBrowserAgent
from core.reach.vision_analyzer import ReachVisionAnalyzer
from core.reach.reader import ReachReader

class ReachFeedEngine:
    """
    Coordinates Agent Reach visual scanning, feed monitoring, post grounding,
    and automated database logging for the LinkedIn Nexus Agent.
    """

    def __init__(
        self,
        browser_agent: Optional[LinkedInBrowserAgent] = None,
        vision_analyzer: Optional[ReachVisionAnalyzer] = None,
        reader: Optional[ReachReader] = None
    ):
        self.browser_agent = browser_agent or LinkedInBrowserAgent(headless=True)
        self.vision = vision_analyzer or ReachVisionAnalyzer()
        self.reader = reader or ReachReader(self.browser_agent)

    def scan_and_log_feed(self, limit: int = 10) -> Dict[str, Any]:
        """
        Executes a live feed scan via Playwright, persists captured posts
        to the SQLite database, and returns the result.
        """
        res = self.browser_agent.scan_feed(limit=limit, capture_screenshot=True)
        if res.get("status") != "success":
            return res

        posts = res.get("posts", [])
        screenshot_url = res.get("screenshot_url")
        screenshot_path = res.get("screenshot_path")

        # Save to database
        conn = get_connection()
        cursor = conn.cursor()
        saved_count = 0

        for p in posts:
            author = p.get("author_name", "LinkedIn Member")
            headline = p.get("author_headline", "")
            text = p.get("post_text", "")
            urn = p.get("post_urn", "")
            reactions = int(str(p.get("reaction_count", 0)).replace(",", "").split()[0]) if str(p.get("reaction_count", 0)).replace(",", "").split()[0].isdigit() else 0
            comments = int(str(p.get("comment_count", 0)).replace(",", "").split()[0]) if str(p.get("comment_count", 0)).replace(",", "").split()[0].isdigit() else 0

            # Avoid duplicates within recent scans
            cursor.execute(
                "SELECT id FROM scanned_feed_posts WHERE post_text = ? LIMIT 1",
                (text,)
            )
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO scanned_feed_posts (
                        author_name, author_headline, post_text, post_url,
                        reaction_count, comment_count, screenshot_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (author, headline, text, urn, reactions, comments, screenshot_url))
                saved_count += 1

        conn.commit()
        conn.close()

        # Run vision analysis on screenshot if present
        vision_summary = None
        if screenshot_path and os.path.exists(screenshot_path):
            vision_res = self.vision.analyze_screenshot(screenshot_path)
            vision_summary = vision_res.get("analysis")

        return {
            "status": "success",
            "posts_found": len(posts),
            "new_posts_saved": saved_count,
            "screenshot_url": screenshot_url,
            "vision_analysis": vision_summary,
            "posts": posts
        }

    def get_recent_scanned_posts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves stored feed posts from SQLite."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, author_name, author_headline, post_text, post_url,
                   reaction_count, comment_count, screenshot_path, scanned_at
            FROM scanned_feed_posts
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def inspect_url(self, url: str) -> Dict[str, Any]:
        """Reads and analyzes any external article, LinkedIn post, or profile URL."""
        return self.reader.read_url(url)
