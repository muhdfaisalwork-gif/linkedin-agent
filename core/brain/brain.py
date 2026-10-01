from typing import List, Dict, Any, Optional
from core.db.database import get_connection

class BrainManager:
    """Manages the agent's long-term memory, story bank, voice fingerprint, and evolving heuristics."""

    def __init__(self):
        pass

    # ---- STORY BANK (Receipts & Projects) ----
    def get_story_bank(self) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM story_bank ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_all_stories(self) -> List[Dict[str, Any]]:
        """Alias for get_story_bank for MCP and external callers."""
        return self.get_story_bank()

    def get_relevant_stories(self, topic: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Returns list of matching story dicts for MCP and search queries."""
        stories = self.get_story_bank()
        if not topic or not stories:
            return stories[:limit]
        topic_words = set(topic.lower().split())
        scored = []
        for s in stories:
            score = 0
            text = f"{s.get('title', '')} {s.get('detail', '')} {s.get('tags', '')} {s.get('category', '')}".lower()
            for w in topic_words:
                if len(w) > 3 and w in text:
                    score += 2
            scored.append((score, s))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:limit]]

    def add_story(self, category: str, title: str, detail: str, metrics: str = "", url: str = "", year_or_date: str = "", tags: str = "") -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO story_bank (category, title, detail, metrics_receipts, url, year_or_date, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (category, title, detail, metrics, url, year_or_date, tags))
        conn.commit()
        story_id = cursor.lastrowid
        conn.close()
        return story_id

    def delete_story(self, story_id: int) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM story_bank WHERE id = ?", (story_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    def update_story(self, story_id: int, category: str, title: str, detail: str, metrics: str = "", url: str = "", year_or_date: str = "", tags: str = "") -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE story_bank
            SET category = ?, title = ?, detail = ?, metrics_receipts = ?, url = ?, year_or_date = ?, tags = ?
            WHERE id = ?
        ''', (category, title, detail, metrics, url, year_or_date, tags, story_id))
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated

    def get_relevant_receipts(self, topic: str, limit: int = 3) -> str:
        """Finds the most relevant projects/receipts from Story Bank to ground LLM drafts in reality."""
        stories = self.get_story_bank()
        if not stories:
            return ""

        topic_words = set(topic.lower().split())
        scored = []
        for s in stories:
            score = 0
            text = f"{s['title']} {s['detail']} {s['tags']} {s['category']}".lower()
            for w in topic_words:
                if len(w) > 3 and w in text:
                    score += 2
            scored.append((score, s))

        scored.sort(key=lambda x: x[0], reverse=True)
        chosen = [item[1] for item in scored[:limit]]

        lines = ["## AUTHENTIC STORY BANK RECEIPTS (USE REAL FACTS, NEVER INVENT):"]
        for c in chosen:
            receipt = f"- **{c['title']}** ({c['year_or_date']}): {c['detail']}"
            if c.get('metrics_receipts'):
                receipt += f" | Concrete receipts: {c['metrics_receipts']}"
            if c.get('url'):
                receipt += f" | Live link: {c['url']}"
            lines.append(receipt)

        return "\n".join(lines)

    # ---- VOICE PROFILE ----
    def get_voice_profile(self) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM voice_profile ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return {
            "tone": "Direct, experienced founder and builder, concrete facts",
            "cadence": "1-2 sentence paragraphs with whitespace",
            "preferred_phrases": "built, shipped, engineered, measured, deployed",
            "banned_phrases": "delve, pivotal, robust, landscape, foster, leverage",
            "cta_style": "Specific question or closing numbered receipt",
            "author_bio": "Founder & Software Architect"
        }

    def update_voice_profile(self, tone: str, cadence: str, preferred: str, banned: str, cta_style: str, bio: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE voice_profile
            SET tone = ?, cadence = ?, preferred_phrases = ?, banned_phrases = ?, cta_style = ?, author_bio = ?
            WHERE id = (SELECT id FROM voice_profile ORDER BY id DESC LIMIT 1)
        ''', (tone, cadence, preferred, banned, cta_style, bio))
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO voice_profile (tone, cadence, preferred_phrases, banned_phrases, cta_style, author_bio)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (tone, cadence, preferred, banned, cta_style, bio))
        conn.commit()
        conn.close()

    # ---- HEURISTICS & WIN-RATES ----
    def get_heuristics(self) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM heuristics ORDER BY weight DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def record_post_performance(self, post_id: int, impressions: int, likes: int, comments: int, reposts: int, saves: int):
        conn = get_connection()
        cursor = conn.cursor()

        # Ensure referenced post exists to satisfy foreign key integrity
        cursor.execute("SELECT id, hook_formula FROM posts WHERE id = ?", (post_id,))
        post = cursor.fetchone()
        if not post:
            cursor.execute('''
                INSERT INTO posts (id, topic, hook_formula, content, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (post_id, "Simulated Architecture Post", "F7 - Odd-Precision Money Ledger", "Simulated build post content", "published"))
            conn.commit()
            cursor.execute("SELECT id, hook_formula FROM posts WHERE id = ?", (post_id,))
            post = cursor.fetchone()

        # Log analytics snapshot
        cursor.execute('''
            INSERT INTO post_analytics (post_id, impressions, likes, comments, reposts, saves)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (post_id, impressions, likes, comments, reposts, saves))
        if post and post["hook_formula"]:
            import re
            match = re.search(r'\b(F\d+|A\d+)\b', post["hook_formula"])
            code = match.group(1) if match else post["hook_formula"].split()[0].strip().rstrip(":-")
            cursor.execute("SELECT * FROM heuristics WHERE formula_code = ?", (code,))
            h = cursor.fetchone()
            if h:
                # Calculate engagement rate = (likes + comments*2 + reposts*3 + saves*2) / max(1, impressions)
                eng_points = likes + (comments * 2.5) + (reposts * 3) + (saves * 2)
                rate = (eng_points / max(1, impressions)) * 100.0 if impressions > 0 else (eng_points * 0.1)

                new_count = h["usage_count"] + 1
                new_avg = ((h["avg_engagement_rate"] * h["usage_count"]) + rate) / new_count

                # Dynamic weight evolution (Bayesian adjustment)
                weight_delta = 0.05 if rate > 2.5 else (-0.03 if rate < 1.0 else 0.01)
                new_weight = round(max(0.5, min(2.5, h["weight"] + weight_delta)), 2)

                cursor.execute('''
                    UPDATE heuristics
                    SET usage_count = ?, avg_engagement_rate = ?, weight = ?, last_evolved = CURRENT_TIMESTAMP
                    WHERE formula_code = ?
                ''', (new_count, round(new_avg, 2), new_weight, code))

        conn.commit()
        conn.close()
