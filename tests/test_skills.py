import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.skills.post_writer import HOOK_FORMULAS, FOUNDER_ANGLES
from core.skills.reply_handler import ReplyHandler

def test_hook_formulas_count():
    assert len(HOOK_FORMULAS) == 20
    assert "F7" in HOOK_FORMULAS
    assert "F17" in HOOK_FORMULAS

def test_founder_angles_count():
    assert len(FOUNDER_ANGLES) == 10
    assert "A1" in FOUNDER_ANGLES
    assert "A10" in FOUNDER_ANGLES

def test_comment_filtering():
    # Mock ReplyHandler without LLM for filtering test
    handler = ReplyHandler(llm=None, brain=None)
    comments = [
        {"author": "Real User", "text": "What database are you using for the high concurrency stream?"},
        {"author": "Bot 1", "text": "great post thanks for sharing"},
        {"author": "Bot 2", "text": "100% agree"}
    ]
    actionable, filtered = handler.filter_comments(comments)
    assert len(actionable) == 1
    assert len(filtered) == 2
    assert actionable[0]["author"] == "Real User"

if __name__ == "__main__":
    test_hook_formulas_count()
    test_founder_angles_count()
    test_comment_filtering()
    print("All Skills tests passed successfully!")
