from typing import Dict, Any, List
from core.llm.client import OpenRouterClient
from core.rules.rules_engine import RulesEngine
from core.rules.humanizer import Humanizer

class EngagerAnalytics:
    def __init__(self, llm: OpenRouterClient):
        self.llm = llm

    def segment_engagers(self, engagers_list: List[Dict[str, str]]) -> Dict[str, Any]:
        """Segments post likers and commenters by ICP fit: prospect, peer, aspirational."""
        prospects = []
        peers = []
        aspirational = []

        prospect_keywords = ["vp", "director", "head of", "chief", "cto", "ceo", "founder", "product manager", "owner"]
        peer_keywords = ["engineer", "developer", "architect", "programmer", "builder"]

        for e in engagers_list:
            title = e.get("title", "").lower()
            name = e.get("name", "Unknown")
            if any(k in title for k in prospect_keywords):
                prospects.append({"name": name, "title": e.get("title"), "category": "High-Value Prospect"})
            elif any(k in title for k in peer_keywords):
                peers.append({"name": name, "title": e.get("title"), "category": "Builder Peer"})
            else:
                aspirational.append({"name": name, "title": e.get("title"), "category": "General Network"})

        return {
            "total_analyzed": len(engagers_list),
            "prospects_count": len(prospects),
            "peers_count": len(peers),
            "prospects": prospects,
            "peers": peers,
            "aspirational": aspirational
        }

class EmployeeAdvocacy:
    def __init__(self, llm: OpenRouterClient):
        self.llm = llm

    def create_advocacy_brief(self, company_update: str) -> Dict[str, Any]:
        """Drafts an employee advocacy package with sample angles and guidelines."""
        update_text = (company_update or "").strip()
        if not update_text:
            update_text = "Raulf International LLC shipped updates across Sultrix Trade OS and Shadow Stream, improving execution latency and streaming stability."

        prompt = f"""Create an Employee Advocacy pack for Raulf International LLC on this update:
"{update_text}"

Provide:
1. Executive Summary & Why this matters
2. 3 Different Angle Drafts for team members (Engineering lead, Product designer, Operations)
3. Brand Guardrails (What NOT to say: no hype, no corporate jargon, share genuine learnings)"""

        system_prompt = RulesEngine.get_system_prompt()
        raw_brief = self.llm.generate_text(prompt, system_prompt=system_prompt, temperature=0.6)
        cleaned_brief, audit = Humanizer.humanize_text(raw_brief)

        return {
            "advocacy_pack": cleaned_brief,
            "audit": audit
        }
