from typing import Dict, Any, List, Optional
from core.llm.client import OpenRouterClient
from core.brain.brain import BrainManager
from core.rules.rules_engine import RulesEngine
from core.rules.humanizer import Humanizer

class InboxHandler:
    def __init__(self, llm: OpenRouterClient, brain: BrainManager):
        self.llm = llm
        self.brain = brain

    def process_message(
        self,
        sender_name: str,
        sender_title: str,
        message_text: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Classifies incoming LinkedIn direct messages and drafts high-converting human replies.
        """
        if not (message_text or "").strip():
            return {
                "sender_name": sender_name or "Unknown",
                "sender_title": sender_title or "LinkedIn Member",
                "intent": "spam_pitch",
                "reply_draft": "Please provide message content to analyze.",
                "audit": {"is_compliant": True, "score": 100}
            }

        voice = self.brain.get_voice_profile()
        stories = self.brain.get_story_bank()
        services_summary = "\n".join([f"- {s['title']}: {s['detail']}" for s in stories[:4]])

        history_str = ""
        if conversation_history:
            history_str = "\n".join([f"{m['sender']}: {m['text']}" for m in conversation_history])

        system_prompt = RulesEngine.get_system_prompt(custom_voice=voice.get("tone", ""))

        prompt = f"""You are handling incoming LinkedIn Direct Messages for a technical founder & software builder.

INBOUND MESSAGE:
From: {sender_name} ({sender_title})
Message: "{message_text}"
{f"Prior Chat History:\n{history_str}" if history_str else ""}

USER'S REAL VENTURES & SERVICES (RAULF INTERNATIONAL LLC):
{services_summary}

YOUR TASK:
1. Classify Intent into one of: 'client_lead', 'partnership', 'recruiter', 'peer_networking', 'spam_pitch'.
2. If it is 'spam_pitch', draft a polite 1-sentence pass or recommendation to ignore.
3. If it is 'client_lead', 'partnership', or 'peer_networking', draft a direct, human, helpful response:
   - Acknowledge their specific question without generic pleasantries ("Hope this finds you well").
   - State how we approach that problem using real systems (Sultrix Trade, Shadow Stream, Shadow Voice, AI agents, custom software).
   - Propose a clean next step (e.g. short 15-min call or specific async question).
4. Tone: Confident, plainspoken builder, no marketing fluff. Under 100 words.

Format your response exactly as:
INTENT: [category]
REPLY: [reply draft]"""

        raw_res = self.llm.generate_text(prompt, system_prompt=system_prompt, temperature=0.6)

        # Parse intent and reply using case-insensitive regex
        import re
        intent = "client_lead"
        reply_draft = raw_res
        
        intent_match = re.search(r'\*{0,2}INTENT:\*{0,2}\s*([^\n\r]+)', raw_res, re.IGNORECASE)
        reply_match = re.search(r'\*{0,2}REPLY:\*{0,2}\s*([\s\S]+)', raw_res, re.IGNORECASE)

        if intent_match:
            intent_raw = intent_match.group(1).strip().lower().replace("*", "").replace("'", "").replace('"', "")
            if "client" in intent_raw or "lead" in intent_raw or "inquiry" in intent_raw:
                intent = "client_lead"
            elif "partner" in intent_raw:
                intent = "partnership"
            elif "recruit" in intent_raw or "job" in intent_raw or "hiring" in intent_raw:
                intent = "recruiter"
            elif "peer" in intent_raw or "network" in intent_raw:
                intent = "peer_networking"
            elif "spam" in intent_raw or "pitch" in intent_raw:
                intent = "spam_pitch"
            else:
                intent = intent_raw.replace(" ", "_")
        if reply_match:
            reply_draft = reply_match.group(1).strip()

        cleaned_reply, audit = Humanizer.humanize_text(reply_draft)

        return {
            "sender_name": sender_name,
            "sender_title": sender_title,
            "intent": intent,
            "reply_draft": cleaned_reply,
            "audit": audit
        }
