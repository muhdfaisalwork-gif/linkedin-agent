import re
from typing import Dict, Any, Optional
from core.llm.client import OpenRouterClient
from core.rules.rules_engine import RulesEngine
from core.rules.humanizer import Humanizer
from core.brain.brain import BrainManager
from core.media.image_generator import ImageGenerator

HOOK_FORMULAS = {
    "F1": {"name": "Platform Risk Anaphora", "best_for": "Category/platform shifts, product-as-fix", "multiplier": "4,240 eng"},
    "F2": {"name": "R.I.P. Obituary", "best_for": "Era-ending claims, industry pivots", "multiplier": "3,822 eng"},
    "F3": {"name": "Year-over-Year Pivot", "best_for": "Identity shifts, founder reflection", "multiplier": "3.74x reach"},
    "F4": {"name": "Time-Anchor Confession", "best_for": "Specific dated lessons, scars", "multiplier": "1,519+ eng"},
    "F5": {"name": "Self-Proving Meta", "best_for": "Public tests, commitment posts", "multiplier": "1,082 eng"},
    "F6": {"name": "Comment-Gate Lead Magnet", "best_for": "Real deliverable, high caution in 2026", "multiplier": "717-3,008 eng"},
    "F7": {"name": "Odd-Precision Money Ledger", "best_for": "+34% reach, strongest opener, number-first", "multiplier": "9.4x reach"},
    "F8": {"name": "Paid-vs-Free Reversal", "best_for": "Free framework giveaway, high multiplier", "multiplier": "19.64x reach"},
    "F9": {"name": "Curiosity-Gap Teaser", "best_for": "Behind the scenes, pays off in 2 lines", "multiplier": "4.25x reach"},
    "F10": {"name": "Contrarian + Historical Receipts", "best_for": "Sacred-cow takes, engineering cycles", "multiplier": "3,083 eng"},
    "F11": {"name": "Emotional Cold-Open", "best_for": "Real story with emotional stakes", "multiplier": "High reach"},
    "F12": {"name": "Permission Slip", "best_for": "Dated facts only, anti-platitude", "multiplier": "Comments"},
    "F13": {"name": "Bait-and-Switch Reversal", "best_for": "Policy or process upgrade", "multiplier": "High reach"},
    "F14": {"name": "Named Gratitude / Tribute", "best_for": "Team and mentor tributes", "multiplier": "Reposts"},
    "F15": {"name": "Explain-to-Kids", "best_for": "Demystifying tech jargon into plain words", "multiplier": "Saves"},
    "F16": {"name": "Status-Strip Humility", "best_for": "Senior voice wanting warmth not distance", "multiplier": "Likes"},
    "F17": {"name": "Controlled A/B Anecdote", "best_for": "One-variable engineering comparison", "multiplier": "Structural"},
    "F18": {"name": "False-Binary Dissolve", "best_for": "Both obvious answers fail", "multiplier": "Structural"},
    "F19": {"name": "Anecdote-Meets-Evidence Bridge", "best_for": "Personal noticing + data stack", "multiplier": "Structural"},
    "F20": {"name": "Diverging-Curves Close", "best_for": "Two trajectories that diverge", "multiplier": "Structural"}
}

FOUNDER_ANGLES = {
    "A1": "Reprice the category: show what incumbent tools cost vs what lean engineering costs",
    "A2": "Content-to-pipeline: the unvarnished engineering build log that generated client inbound",
    "A3": "Audience of one: write specifically for the technical VP or founder who hires you",
    "A4": "The scarce-shots math: how early-stage builders survive high-risk bets",
    "A5": "The unglamorous bet: boring architecture choices that saved thousands in cloud bills",
    "A6": "The limit of delegation: what a founder must build themselves before hiring",
    "A7": "Designed serendipity: shipping prototypes daily until something hits market friction",
    "A8": "The evasive-sentence test: calling out software industry buzzwords with working code",
    "A9": "The delegation line: exact boundary between human judgment and autonomous AI agents",
    "A10": "The learning gate: real scars from shipping voice agents, trading OS, and streaming apps"
}

class PostWriter:
    def __init__(self, llm: OpenRouterClient, brain: BrainManager):
        self.llm = llm
        self.brain = brain

    def draft_post(
        self,
        topic: str,
        hook_code: str = "F7",
        founder_angle_code: Optional[str] = None,
        target_length: str = "medium",
        visual_type: str = "ai_image"
    ) -> Dict[str, Any]:
        """
        Drafts a full LinkedIn post with text + image adhering strictly to the 82 rules.
        """
        formula = HOOK_FORMULAS.get(hook_code, HOOK_FORMULAS["F7"])
        angle_desc = FOUNDER_ANGLES.get(founder_angle_code, "") if founder_angle_code else ""

        # Retrieve relevant receipts from the Story Bank
        story_receipts = self.brain.get_relevant_receipts(topic)
        voice = self.brain.get_voice_profile()

        length_guide = "900 to 1,300 characters (LinkedIn sweet spot)"
        if target_length == "short":
            length_guide = "400 to 600 characters"
        elif target_length == "long":
            length_guide = "1,500 to 1,800 characters"

        system_prompt = RulesEngine.get_system_prompt(
            custom_voice=f"Author Bio: {voice.get('author_bio')}\nTone: {voice.get('tone')}\nPreferred verbs: {voice.get('preferred_phrases')}"
        )

        user_prompt = f"""Write a LinkedIn post about: {topic}

HOOK FORMULA: {hook_code} - {formula['name']} ({formula['best_for']})
{f"FOUNDER ANGLE: {angle_desc}" if angle_desc else ""}
TARGET LENGTH: {length_guide}

{story_receipts}

MANDATORY STRUCTURAL REQUIREMENTS:
1. LINE 1 (HOOK): Under 210 characters. NEVER open with a question (-34% reach penalty). Start with a concrete fact or number (+34% reach).
2. BODY: 1-2 sentence paragraphs with clean blank line breaks for mobile readers.
3. CONCRETE EVIDENCE: Include at least one real project, tool, number, or timeline from the Story Bank above (e.g. Sultrix Trade OS, Shadow Stream, Shadow Voice, CRM dashboard, Raulf International).
4. CLOSE: End with a specific question or a dated receipt.
5. NO EXTERNAL LINKS in post text (they belong in first comment).
6. 0 to 2 hashtags at the very bottom.
7. STRICT RULE ENFORCEMENT: No AI buzzwords (delve, pivotal, robust, landscape, leverage, streamline). No 'In today's fast-paced world'. No fake sincerity.
8. OUTPUT ONLY THE POST. Do not write 'Here is a draft' or 'The user wants'. Start immediately on line 1 with the post hook."""

        raw_draft = self.llm.generate_text(user_prompt, system_prompt=system_prompt, temperature=0.65)

        # Run Humanizer 4-pass scrub
        cleaned_draft, audit = Humanizer.humanize_text(raw_draft)

        # Generate Visual (AI Flux Art or Typeset Quote-Card)
        hook_line = cleaned_draft.split('\n')[0].strip() if cleaned_draft else topic
        author_bio_str = voice.get("author_bio") or "Founder & Architect"
        author_name = author_bio_str.split(".")[0].strip() or "Founder & Architect"

        visual_info = ImageGenerator.create_post_visual(
            hook=hook_line,
            topic=topic,
            visual_type=visual_type,
            author_name=author_name
        )

        return {
            "topic": topic,
            "hook_formula": f"{hook_code} - {formula['name']}",
            "founder_angle": angle_desc,
            "raw_content": raw_draft,
            "content": cleaned_draft,
            "image_url": visual_info["url"],
            "image_type": visual_info["type"],
            "audit": audit,
            "char_count": len(cleaned_draft),
            "suggested_posting_time": "Tue-Thu 7:30 AM - 9:00 AM local time"
        }
