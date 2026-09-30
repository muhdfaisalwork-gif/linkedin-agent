import re
from typing import Dict, Any, List, Optional, Tuple
from core.llm.client import OpenRouterClient
from core.brain.brain import BrainManager
from core.rules.rules_engine import RulesEngine
from core.rules.humanizer import Humanizer

REPLY_TEMPLATES = {
    "R1": "Answer-Their-Question: Answer directly with 1 concrete technical or operational detail.",
    "R2": "Concede-Then-Sharpen: 'You are right on X, and the piece I would push on is Y.'",
    "R3": "Extend-Their-Thesis: Take their point one layer deeper with a fresh angle.",
    "R4": "Share-Lived-Experience: 'We hit this when shipping Sultrix/Shadow Stream—here is what broke.'",
    "R5": "Ask-Back: Redirect with a sharper follow-up question when their position needs context."
}

class ReplyHandler:
    def __init__(self, llm: OpenRouterClient, brain: BrainManager):
        self.llm = llm
        self.brain = brain

    def filter_comments(self, comments: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filters out low-value comments (generic 'great post', spam, self-comments)
        Returns (actionable_comments, filtered_out)
        """
        actionable = []
        filtered_out = []

        low_value_patterns = [
            r"\b(great post|thanks for sharing|helpful|love this|so true|agree|nice|100%|spot on)\b",
            r"check out my (profile|link|service|course)",
            r"http[s]?://",
            r"dm sent"
        ]

        for c in comments:
            text = c.get("text", "").strip().lower()
            if not text:
                continue

            # Drop if matches low-value pattern
            is_low_value = any(re.search(pat, text) for pat in low_value_patterns)
            if is_low_value and len(text) < 40:
                filtered_out.append({"comment": c, "reason": "Low-value generic praise or spam"})
            else:
                actionable.append(c)

        return actionable, filtered_out

    def draft_reply(
        self,
        original_post: str,
        comment_text: str,
        commenter_name: str,
        depth: int = 1,
        top_level_urn: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Drafts a context-aware, human-natural reply (150-300 characters).
        Handles LinkedIn 2-level flattening rule.
        """
        if not comment_text or not comment_text.strip():
            return {
                "commenter": commenter_name,
                "comment_text": "",
                "reply_draft": "Please provide comment text to generate a reply.",
                "suggested_reaction": "LIKE",
                "depth": depth,
                "parent_comment_urn": None,
                "char_count": 0,
                "audit": {"is_compliant": True, "score": 100}
            }

        voice = self.brain.get_voice_profile()
        system_prompt = RulesEngine.get_system_prompt(custom_voice=voice.get("tone", ""))

        prompt = f"""Draft a reply to this LinkedIn comment:
ORIGINAL POST CONTEXT: {original_post[:300]}...
COMMENT BY {commenter_name}: "{comment_text}"

REQUIREMENTS:
1. Length: 150 to 300 characters. Tight, direct, conversational.
2. Tone: Knowledgeable builder, human, respectful.
3. No canned "Thanks for sharing!" or "Appreciate your thoughts!".
4. If they asked a question, answer it directly with a concrete detail.
5. If they shared a perspective, either extend it or concede and sharpen.
6. Suggest an appropriate reaction (LIKE, PRAISE, or INTEREST).
7. Do not use AI buzzwords."""

        raw_reply = self.llm.generate_text(prompt, system_prompt=system_prompt, temperature=0.6)
        cleaned_reply, audit = Humanizer.humanize_text(raw_reply)

        # Decide reaction
        reaction = "LIKE"
        if "?" in comment_text:
            reaction = "INTEREST"
        elif any(w in comment_text.lower() for w in ["build", "ship", "great", "congrats"]):
            reaction = "PRAISE"

        return {
            "commenter": commenter_name,
            "comment_text": comment_text,
            "reply_draft": cleaned_reply,
            "suggested_reaction": reaction,
            "depth": depth,
            # CRITICAL 2026 LINKEDIN RULE: If depth > 1, parentComment MUST be top-level comment URN!
            "parent_comment_urn": top_level_urn if depth > 1 else None,
            "char_count": len(cleaned_reply),
            "audit": audit
        }
