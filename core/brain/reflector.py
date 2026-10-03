from typing import Dict, Any, List
from core.db.database import get_connection
from core.llm.client import OpenRouterClient
from core.rules.rules_engine import MASTER_WRITING_SYSTEM_PROMPT

class Reflector:
    """Evaluates post performance history and evolves agent strategy."""

    def __init__(self, llm: OpenRouterClient):
        self.llm = llm

    def run_reflection_cycle(self) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()

        # Fetch recent posts with analytics
        cursor.execute('''
            SELECT p.id, p.topic, p.hook_formula, p.content,
                   COALESCE(MAX(a.impressions), 0) as impressions,
                   COALESCE(MAX(a.likes), 0) as likes,
                   COALESCE(MAX(a.comments), 0) as comments,
                   COALESCE(MAX(a.reposts), 0) as reposts
            FROM posts p
            LEFT JOIN post_analytics a ON p.id = a.post_id
            GROUP BY p.id
            ORDER BY p.id DESC LIMIT 15
        ''')
        recent_posts = cursor.fetchall()

        if not recent_posts:
            conn.close()
            return {
                "status": "skipped",
                "title": "Reflection Notice",
                "message": "No published posts available for reflection yet. Draft and publish a post or simulate metrics first."
            }

        posts_summary = []
        for p in recent_posts:
            posts_summary.append(
                f"- Post #{p['id']} [{p['hook_formula']}]: \"{p['topic']}\" | "
                f"{p['impressions']} views, {p['likes']} likes, {p['comments']} comments, {p['reposts']} shares."
            )

        prompt = f"""You are the cognitive self-reflection engine of an autonomous LinkedIn builder agent.
Review these recent post performance records:
{chr(10).join(posts_summary)}

Analyze:
1. Which hook formulas or formats generated the strongest discussion and engagement?
2. Which angles fell flat or had high impression-to-engagement drop-off?
3. What 2 concrete adjustments should the agent make to future drafts?

Respond in concise, plain human sentences. Do not use corporate buzzwords."""

        try:
            reflection_text = self.llm.generate_text(
                prompt,
                system_prompt="You are a senior content engineer evaluating empirical social performance data."
            )

            title = f"Evolution Reflection Cycle - {len(recent_posts)} Posts Analyzed"
            cursor.execute('''
                INSERT INTO reflections (title, learnings, strategy_shifts)
                VALUES (?, ?, ?)
            ''', (title, reflection_text, "Evolved heuristic weights based on empirical engagement."))
            conn.commit()
            conn.close()

            return {
                "status": "success",
                "title": title,
                "analysis": reflection_text
            }
        except Exception as e:
            conn.close()
            return {"status": "error", "message": str(e)}

    def get_reflection_history(self) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reflections ORDER BY created_at DESC LIMIT 20")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
