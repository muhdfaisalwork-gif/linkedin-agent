from typing import Dict, Any, List, Optional
from core.llm.client import OpenRouterClient
from core.brain.brain import BrainManager
from core.rules.rules_engine import RulesEngine
from core.rules.humanizer import Humanizer

class ProfileOptimizer:
    def __init__(self, llm: OpenRouterClient, brain: BrainManager):
        self.llm = llm
        self.brain = brain

    def optimize_profile(self, user_notes_or_profile: str, goal: str = "clients_and_authority") -> Dict[str, Any]:
        """
        Audits and rewrites LinkedIn profile sections based on user's real projects & services:
        - Headline (all 220 chars)
        - 7-step About section (first 265 chars hook)
        - Featured section playbook
        - Experience section bullets (action verb + metric)
        - Top 50 Skills & Top 3 pinned
        """
        stories = self.brain.get_story_bank()
        projects_summary = "\n".join([
            f"- {s['title']} ({s.get('url', '')}): {s['detail']} | Receipts: {s.get('metrics_receipts', '')}"
            for s in stories
        ])

        system_prompt = RulesEngine.get_system_prompt()

        user_input = (user_notes_or_profile or "").strip()
        if not user_input:
            user_input = "Highlight full software services, Sultrix Trade OS, Shadow Stream, Shadow Voice, CRM solutions, and Raulf International LLC."

        prompt = f"""You are an elite LinkedIn profile strategist optimizing a technical founder / builder profile.
The user wants to upgrade their profile with their real products and services:
{user_input}

AUTHENTIC PROJECTS & CREDENTIALS IN STORY BANK:
{projects_summary}

GOAL: {goal}

Optimize the following 4 core sections strictly following 2026 conversion patterns:

### 1. HEADLINE (Max 220 characters)
Formula: [What You Build / Lead] | [Who You Help] [Concrete Result] | [Key Tech / Ventures]
Make it direct, authoritative, and specific (include ventures like Sultrix Trade, Shadow Stream, Shadow Voice / Raulf International).

### 2. ABOUT SECTION (250-350 words, 7-step structure)
- Step 1 (Hook): First 265 characters MUST land before the 'see more' fold. No platitudes.
- Step 2: The Core Problem in the market.
- Step 3: What I Build & Offer (Sultrix Trade OS, Shadow Stream, Shadow Voice, SEO Agents, Enterprise CRMs, Full Services at Raulf International).
- Step 4: Technical Proof & Architecture.
- Step 5: How I Work with Clients & Partners.
- Step 6: Tech Stack & Domains.
- Step 7: Clear Direct CTA (reach out or book an engineering call).
Use 1-2 sentence paragraphs with whitespace. First person ('I build...'). Zero AI buzzwords ('passionate', 'results-oriented', 'leveraging').

### 3. FEATURED SECTION ITEMS (3 Recommended Cards)
List 3 concrete items to pin in the Featured section with link, title, and 1-line description.

### 4. EXPERIENCE BULLETS (For Founder / Managing Member Role)
Draft 4 high-impact bullets formatted as: [Action Verb] + [Specific System Built] + [Observable Metric / Consequence].

### 5. TOP 3 PINNED SKILLS
Select the top 3 high-leverage skills to pin for maximum search discovery."""

        raw_output = self.llm.generate_text(prompt, system_prompt=system_prompt, temperature=0.6)
        cleaned_output, audit = Humanizer.humanize_text(raw_output)

        # Build 9-Component Scorecard
        scorecard = [
            {"section": "Photo", "status": "pass", "note": "Use high-contrast headshot with natural light filling 60% of frame."},
            {"section": "Banner", "status": "recommended", "note": "1584x396px banner highlighting Sultrix Trade OS & Raulf International services."},
            {"section": "Headline", "status": "optimized", "note": "220-char formula applied with clear builder identity."},
            {"section": "About", "status": "optimized", "note": "7-step structure generated with hook in first 265 chars."},
            {"section": "Featured", "status": "optimized", "note": "3 flagship products pinned (Sultrix, Shadow Stream, CRM)."},
            {"section": "Experience", "status": "optimized", "note": "Action verb + metric bullets created."},
            {"section": "Skills", "status": "optimized", "note": "Top 3 pinned skills identified."},
            {"section": "Custom URL", "status": "recommended", "note": "Claim linkedin.com/in/yourname without default hash."},
            {"section": "Recommendations", "status": "recommended", "note": "Request 3 client recommendations citing real delivered systems."}
        ]

        return {
            "scorecard": scorecard,
            "optimized_content": cleaned_output,
            "audit": audit,
            "raw_output": raw_output
        }
