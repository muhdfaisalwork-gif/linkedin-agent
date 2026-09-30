from typing import Dict, Any, List
from core.llm.client import OpenRouterClient
from core.brain.brain import BrainManager
from core.rules.rules_engine import RulesEngine
from core.rules.humanizer import Humanizer

class ContentPlanner:
    def __init__(self, llm: OpenRouterClient, brain: BrainManager):
        self.llm = llm
        self.brain = brain

    def create_weekly_plan(self, focus_topic: str = "AI Agents & High-Concurrency Systems") -> Dict[str, Any]:
        """Creates a 7-day LinkedIn editorial plan mapped to 2026 hook formulas."""
        stories = self.brain.get_story_bank()
        stories_context = "\n".join([f"- {s['title']}: {s['detail']}" for s in stories[:5]])

        system_prompt = RulesEngine.get_system_prompt()

        prompt = f"""Create a 7-day strategic LinkedIn content calendar.
Primary Domain / Focus: {focus_topic}

USER'S REAL BUILDS (STORY BANK):
{stories_context}

CONTENT PILLARS FOR 2026:
- Pillar 1: Conviction & Sacred Cow takes (Engineering contrarian opinions)
- Pillar 2: Building in Public (Sultrix Trade OS, Shadow Stream architecture, real bugs fixed)
- Pillar 3: The Math & Ledgers (Odd-precision cost breakdowns, cloud bills cut, latency reduced)
- Pillar 4: Proof & Client Case Studies (CRM dashboards, Relyguru, Raulf International services)

For each of the 7 days (Monday through Sunday), output:
Day X:
- Format: Text + Image (AI art or quote card)
- Pillar: [Pillar name]
- Hook Formula: [e.g. F7 Odd-Precision Money Ledger, F17 Controlled A/B, F10 Contrarian Receipts]
- Working Title / Angle: [1 sentence concrete angle]
- Best Time: [e.g. Tuesday 8:00 AM]"""

        raw_plan = self.llm.generate_text(prompt, system_prompt=system_prompt, temperature=0.7)
        cleaned_plan, audit = Humanizer.humanize_text(raw_plan)

        return {
            "focus_topic": focus_topic,
            "weekly_plan": cleaned_plan,
            "audit": audit
        }
