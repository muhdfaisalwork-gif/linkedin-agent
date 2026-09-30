from typing import Dict, Any
from core.llm.client import OpenRouterClient
from core.rules.rules_engine import RulesEngine
from core.rules.humanizer import Humanizer

class HookExtractor:
    def __init__(self, llm: OpenRouterClient):
        self.llm = llm

    def extract_hook(self, post_text: str) -> Dict[str, Any]:
        """Reverse-engineers a viral post's hook into a blank structural formula."""
        text = (post_text or "").strip()
        if not text:
            return {
                "source_sample": "",
                "formula_breakdown": "Please provide post text to extract a hook formula.",
                "audit": {"is_compliant": True, "score": 100}
            }

        prompt = f"""Analyze this viral LinkedIn post and extract its underlying hook formula:
"{text}"

Return:
1. Hook Category & Formula Name (e.g. False-Binary Dissolve, Odd-Precision Ledger, Emotional Cold-Open)
2. Why It Works (Empirical cognitive trigger)
3. Blank Fill-in-the-Blank Template for a builder/founder to use with their own topic."""

        system_prompt = RulesEngine.get_system_prompt()
        analysis = self.llm.generate_text(prompt, system_prompt=system_prompt, temperature=0.5)
        cleaned_analysis, audit = Humanizer.humanize_text(analysis)

        return {
            "source_sample": text[:200] + "...",
            "formula_breakdown": cleaned_analysis,
            "audit": audit
        }

class Repurposer:
    def __init__(self, llm: OpenRouterClient):
        self.llm = llm

    def repurpose_to_linkedin(self, source_text: str, source_type: str = "tweet") -> Dict[str, Any]:
        """Repurposes external content (tweet thread, blog, video transcript) to native LinkedIn format."""
        text = (source_text or "").strip()
        if not text:
            return {
                "source_type": source_type,
                "repurposed_post": "Please provide source content to repurpose.",
                "char_count": 0,
                "audit": {"is_compliant": True, "score": 100}
            }

        prompt = f"""Convert this {source_type} into a high-performing native LinkedIn post:
"{text}"

LINKEDIN 2026 SPECIFICATIONS:
- Length: 900-1300 characters
- Hook in first 210 characters (statement or number, never a question)
- 1-2 sentence paragraphs with whitespace
- Strip external links (they go to first comment)
- End with a specific technical question
- Follow the 82 rules: no AI buzzwords, concrete plain verbs."""

        system_prompt = RulesEngine.get_system_prompt()
        raw_post = self.llm.generate_text(prompt, system_prompt=system_prompt, temperature=0.6)
        cleaned_post, audit = Humanizer.humanize_text(raw_post)

        return {
            "source_type": source_type,
            "repurposed_post": cleaned_post,
            "char_count": len(cleaned_post),
            "audit": audit
        }
