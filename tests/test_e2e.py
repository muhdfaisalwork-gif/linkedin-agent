import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from core.db.database import init_db
from core.llm.client import OpenRouterClient
from core.brain.brain import BrainManager
from core.skills.post_writer import PostWriter
from core.skills.profile_optimizer import ProfileOptimizer
from core.skills.reply_handler import ReplyHandler

def test_full_pipeline():
    init_db()
    llm = OpenRouterClient()
    brain = BrainManager()

    print("[1] Testing OpenRouter connectivity & free model routing...")
    test_res = llm.generate_text("Respond with: PIPELINE_ONLINE", temperature=0.2)
    print("    OpenRouter Response:", test_res[:50])
    assert len(test_res) > 0

    print("[2] Testing Post Writer with Story Bank grounding (Sultrix Trade OS)...")
    writer = PostWriter(llm, brain)
    post = writer.draft_post(
        topic="Architecture lessons from building Sultrix Trade OS and cutting order latency",
        hook_code="F7",
        founder_angle_code="A5",
        target_length="medium",
        visual_type="quote_card"
    )
    print("    Hook line:", post["content"].split("\n")[0])
    print("    Audit Score:", post["audit"]["score"])
    print("    Visual URL:", post["image_url"])
    assert len(post["content"]) > 100
    assert post["audit"]["is_compliant"] or post["audit"]["score"] >= 80

    print("[3] Testing Profile Optimizer with user's ventures...")
    optimizer = ProfileOptimizer(llm, brain)
    profile_res = optimizer.optimize_profile(
        user_notes_or_profile="Highlight Sultrix Trade OS, Shadow Stream, Shadow Voice, and Raulf International services."
    )
    print("    Headline & About generated successfully!")
    assert "Headline" in profile_res["optimized_content"] or "HEADLINE" in profile_res["optimized_content"]
    assert len(profile_res["scorecard"]) == 9

    print("\n[OK] All End-to-End Pipeline tests completed successfully!")

if __name__ == "__main__":
    test_full_pipeline()
