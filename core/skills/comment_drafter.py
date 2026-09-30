from typing import Dict, Any
from core.llm.client import OpenRouterClient
from core.brain.brain import BrainManager
from core.rules.rules_engine import RulesEngine
from core.rules.humanizer import Humanizer

class CommentDrafter:
    def __init__(self, llm: OpenRouterClient, brain: BrainManager):
        self.llm = llm
        self.brain = brain

    def draft_comment(self, post_text: str, author_name: str = "Author") -> Dict[str, Any]:
        """Drafts a high-visibility, thoughtful comment on someone else's LinkedIn post."""
        text = (post_text or "").strip()
        if not text:
            return {
                "author_target": author_name,
                "comment_draft": "Please provide post text to draft a thoughtful comment.",
                "char_count": 0,
                "audit": {"is_compliant": True, "score": 100}
            }

        voice = self.brain.get_voice_profile()
        system_prompt = RulesEngine.get_system_prompt(custom_voice=voice.get("tone", ""))

        prompt = f"""Draft a thoughtful, high-value LinkedIn comment on this post by {author_name}:
"{post_text}"

CRITICAL RULES:
1. Length: 200-350 characters.
2. Deliver ONE sharp, concrete insight or an empirical nuance from real builder experience.
3. NEVER say "Great post!", "Insightful read!", or "Couldn't agree more!".
4. No self-promotional pitches or unsolicited links.
5. Do not use AI buzzwords (delve, pivotal, robust, landscape, leverage).
6. Plain human conversational tone."""

        raw_comment = self.llm.generate_text(prompt, system_prompt=system_prompt, temperature=0.6)
        cleaned_comment, audit = Humanizer.humanize_text(raw_comment)

        return {
            "author_target": author_name,
            "comment_draft": cleaned_comment,
            "char_count": len(cleaned_comment),
            "audit": audit
        }
